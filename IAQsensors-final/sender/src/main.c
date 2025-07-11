#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdarg.h>

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include "sensor/sps30/sps30.h"
#include <zephyr/sys/printk.h>
#include <zephyr/logging/log.h>
#include <zephyr/drivers/sensor/ccs811.h>
#include "sensor/scd4x/scd4x.h"

#include <openthread/coap.h>
#include <openthread/ip6.h>
#include <openthread/thread.h>
#include <openthread/instance.h>

LOG_MODULE_REGISTER(sensor_coap, LOG_LEVEL_INF);

#if !DT_HAS_COMPAT_STATUS_OKAY(sensirion_scd41)
#error "No sensirion,scd4x compatible node found in the device tree"
#endif

#if !DT_HAS_COMPAT_STATUS_OKAY(sensirion_sps30)
#error "No sensirion,sps30 compatible node found in the device tree"
#endif

#define SLEEP_TIME_MS 30000 //30s
#define SENSOR_JSON_BUF_SIZE 256
#define MAX_COAP_RETRIES 5

static char json_buf[SENSOR_JSON_BUF_SIZE];

// Sensor devices
static const struct device *scd41 = DEVICE_DT_GET_ANY(sensirion_scd41);
static const struct device *ccs811 = DEVICE_DT_GET_ANY(ams_ccs811);
static const struct device *sps30 = DEVICE_DT_GET_ANY(sensirion_sps30);

static void coap_send_data_request(const char *data);
static void coap_send_data_response_cb(void *context, otMessage *message,
                                       const otMessageInfo *message_info, otError result);
void coap_init(void);

bool build_json(char *buf, size_t buf_size, const char *format, ...) {
    va_list args;
    va_start(args, format);

    int written = vsnprintf(buf, buf_size, format, args);
    va_end(args);

    if (written < 0 || (size_t)written >= buf_size) {
        snprintf(buf, buf_size, "{\"error\":\"json_truncated\"}");
        return false;  // Indicates truncation or error
    }

    return true; // JSON was safely written
}

// Helper: safely build JSON and send via CoAP
static void send_json_or_error(const char *sensor_name, int err, int json_len) {
    if (err) {
        LOG_ERR("%s sensor error: %d", sensor_name, err);
        snprintf(json_buf, sizeof(json_buf), "{\"error\":\"%s read failed: %d\"}", sensor_name, err);
    } else if (json_len < 0 || json_len >= sizeof(json_buf)) {
        LOG_ERR("%s JSON overflow or format error (%d bytes)", sensor_name, json_len);
        snprintf(json_buf, sizeof(json_buf), "{\"error\":\"%s JSON out of bounds\"}", sensor_name);
    }
    coap_send_data_request(json_buf);
}

// value = val1 + val2 * 10^-6 is the convention for sensor_value in Zephyr
static void read_and_send_scd41(void) {
    struct sensor_value co2, temp, humi;
    int err = sensor_sample_fetch(scd41);
    if (!err) err = sensor_channel_get(scd41, SENSOR_CHAN_CO2_SCD, &co2);
    if (!err) err = sensor_channel_get(scd41, SENSOR_CHAN_AMBIENT_TEMP, &temp);
    if (!err) err = sensor_channel_get(scd41, SENSOR_CHAN_HUMIDITY, &humi);

    int json_len = 0;
    bool ok = false;

    if (!err) {
            ok = build_json(json_buf, sizeof(json_buf),
                "{\"co2\":%d,\"temp\":\"%d.%01d\",\"humi\":\"%d.%01d\"}",
                co2.val1,
                temp.val1, temp.val2,
                humi.val1, humi.val2
            );
        }
    send_json_or_error("SCD41", err, ok ? json_len : -1);
}

static void read_and_send_ccs811(void) {
    struct sensor_value eco2, tvoc;
    int err = sensor_sample_fetch(ccs811);
    if (!err) err = sensor_channel_get(ccs811, SENSOR_CHAN_CO2, &eco2);
    if (!err) err = sensor_channel_get(ccs811, SENSOR_CHAN_VOC, &tvoc);

    int json_len = 0;
    bool ok = false;

    if (!err) {
        
        ok = build_json(json_buf, sizeof(json_buf),
            "{\"eco2\":%d,\"tvoc\":%d}",
            eco2.val1, 
            tvoc.val1
            );
        json_len = strlen(json_buf);
    }
    send_json_or_error("CCS811", err, ok ? json_len : -1);
}

static void read_and_send_sps30(void) {
    struct sensor_value pm_2p5, pm_10p0, typical_particle_size;
    int err = sensor_sample_fetch(sps30);
    if (!err) err = sensor_channel_get(sps30, SENSOR_CHAN_PM_2_5, &pm_2p5);
    if (!err) err = sensor_channel_get(sps30, SENSOR_CHAN_PM_10, &pm_10p0);
    if (!err) err = sensor_channel_get(sps30, SENSOR_CHAN_PM_TYPICAL_PARTICLE_SIZE, &typical_particle_size);

    int json_len = 0;
    bool ok = false;

    if (!err) {

        ok = build_json(json_buf, sizeof(json_buf),
            "{\"pm25\":\"%d.%02d\",\"pm10\":\"%d.%02d\",\"typ\":\"%d.%06d\"}",
            pm_2p5.val1, pm_2p5.val2,
            pm_10p0.val1, pm_10p0.val2,
            typical_particle_size.val1, typical_particle_size.val2);
    }
    send_json_or_error("SPS30", err, ok ? json_len : -1);
}

int main(void) {
    printk("Starting CoAP server with sensor data\n");

    coap_init();

    bool scd41_ready = device_is_ready(scd41);
    bool ccs811_ready = device_is_ready(ccs811);
    bool sps30_ready = device_is_ready(sps30);

    if (scd41 == NULL) {
        printk("SCD41 device not found in device tree\n");
        coap_send_data_request("{\"error\":\"SCD41 not found\"}");
    } else if (!device_is_ready(scd41)) {
        printk("SCD41 device found but not ready\n");
        coap_send_data_request("{\"error\":\"SCD41 not ready\"}");
    }
    if (ccs811 == NULL) {
        printk("CCS811 device not found in device tree\n");
        coap_send_data_request("{\"error\":\"CCS811 not found\"}");
    } else if (!device_is_ready(ccs811)) {
        printk("CCS811 device found but not ready\n");
        coap_send_data_request("{\"error\":\"CCS811 not ready\"}");
    }
    if (sps30 == NULL) {
        printk("SPS30 device not found in device tree\n");
        coap_send_data_request("{\"error\":\"SPS30 not found\"}");
    } else if (!device_is_ready(sps30)) {
        printk("SPS30 device found but not ready\n");
        coap_send_data_request("{\"error\":\"SPS30 not ready\"}");
    }

    while (1) {
        if (scd41_ready) {
            read_and_send_scd41();
        }
        if (ccs811_ready) {
            read_and_send_ccs811();
        }
        if (sps30_ready) {
            read_and_send_sps30();
        }
        k_msleep(SLEEP_TIME_MS);
    }
}

void coap_init(void) {
    otInstance *instance = openthread_get_default_instance();
    otError error = otCoapStart(instance, OT_DEFAULT_COAP_PORT);
    if (error != OT_ERROR_NONE) {
        printk("Failed to start CoAP: %d\n", error);
    } else {
        printk("CoAP started on port %d\n", OT_DEFAULT_COAP_PORT);
    }
}

static void coap_send_data_response_cb(void *context, otMessage *message,
                                       const otMessageInfo *message_info, otError result) {
    if (result == OT_ERROR_NONE) {
        printk("Delivery confirmed.\n");
    } else {
        printk("Delivery not confirmed: %d\n", result);
    }
}

static void coap_send_data_request(const char *data) {
    otInstance *myInstance = openthread_get_default_instance();
    otMessage *myMessage = NULL;
    otMessageInfo myMessageInfo;
    otError error = OT_ERROR_NONE;
    uint8_t retry = 0;

    const otMeshLocalPrefix *ml_prefix = otThreadGetMeshLocalPrefix(myInstance);
    uint8_t serverInterfaceID[8] = {0, 0, 0, 0, 0, 0, 0, 1};

    while (retry++ < MAX_COAP_RETRIES) {
        myMessage = otCoapNewMessage(myInstance, NULL);

        if (!myMessage) {
            printk("Failed to allocate message for CoAP Request\n");
            return;
        }

        otCoapMessageInit(myMessage, OT_COAP_TYPE_CONFIRMABLE, OT_COAP_CODE_PUT);

        error = otCoapMessageAppendUriPathOptions(myMessage, "storedata");
        if (error != OT_ERROR_NONE) break;

        error = otCoapMessageAppendContentFormatOption(myMessage, OT_COAP_OPTION_CONTENT_FORMAT_JSON);
        if (error != OT_ERROR_NONE) break;

        error = otCoapMessageSetPayloadMarker(myMessage);
        if (error != OT_ERROR_NONE) break;

        error = otMessageAppend(myMessage, data, strlen(data));
        if (error != OT_ERROR_NONE) break;

        memset(&myMessageInfo, 0, sizeof(myMessageInfo));
        memcpy(&myMessageInfo.mPeerAddr.mFields.m8[0], ml_prefix, 8);
        memcpy(&myMessageInfo.mPeerAddr.mFields.m8[8], serverInterfaceID, 8);
        myMessageInfo.mPeerPort = OT_DEFAULT_COAP_PORT;

        error = otCoapSendRequest(myInstance, myMessage, &myMessageInfo, coap_send_data_response_cb, NULL);
        if (error == OT_ERROR_NONE) {
            LOG_INF("CoAP Request sent successfully.\n");
            return; // Exit on success
        } else {
            LOG_INF("CoAP Request send failed: %d, retrying...\n", error);
            otMessageFree(myMessage);
            myMessage = NULL; // Reset to avoid double free
        }
    } 
}