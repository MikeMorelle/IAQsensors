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

#if !DT_HAS_COMPAT_STATUS_OKAY(sensirion_scd41)
#error "No sensirion,scd4x compatible node found in the device tree"
#endif

#if !DT_HAS_COMPAT_STATUS_OKAY(sensirion_sps30)
#error "No sensirion,sps30 compatible node found in the device tree"
#endif

#define SLEEP_TIME_MS 5000
#define SENSOR_JSON_BUF_SIZE 1024
char json_buf[SENSOR_JSON_BUF_SIZE];


const struct device *scd41 = DEVICE_DT_GET_ANY(sensirion_scd41);
const struct device *ccs811 = DEVICE_DT_GET_ANY(ams_ccs811);
const struct device *sps30 = DEVICE_DT_GET_ANY(sensirion_sps30);

// Forward declarations
static void coap_send_data_request(char * data); 
static void coap_send_data_response_cb(void * p_context, otMessage * p_message, 
const otMessageInfo * p_message_info, otError result); 


int main(void)
{
    printk("Starting CoAP server with sensor data\n");
    coap_init();

    bool scd41_ready = device_is_ready(scd41);
    bool ccs811_ready = device_is_ready(ccs811);
    bool sps30_ready = device_is_ready(sps30);

    if (!scd41_ready) {
        printk("SCD41 not ready\n");
        coap_send_data_request("{\"error\": \"SCD41 not ready\"}");
    }

    if (!ccs811_ready) {
        printk("CCS811 not ready\n");
        coap_send_data_request("{\"error\": \"CCS811 not ready\"}");
    }

    if (!sps30_ready) {
        printk("SPS30 not ready\n");
        coap_send_data_request("{\"error\": \"SPS30 not ready\"}");
    }

    struct sensor_value co2, temp, humi;
    struct sensor_value eco2, tvoc;
    struct sensor_value pm_2p5, pm_10p0;

    while (1) {
        int err;
        int json_len;

        // Handle SCD41
        if (scd41_ready) {
            err = sensor_sample_fetch(scd41);
            if (!err) err = sensor_channel_get(scd41, SENSOR_CHAN_CO2_SCD, &co2);
            if (!err) err = sensor_channel_get(scd41, SENSOR_CHAN_AMBIENT_TEMP, &temp);
            if (!err) err = sensor_channel_get(scd41, SENSOR_CHAN_HUMIDITY, &humi);

            if (err) {
                printk("SCD41 error: %d\n", err);
                snprintf(json_buf, sizeof(json_buf), "{\"error\": \"SCD41 read failed: %d\"}", err);
            } else {
                json_len = snprintf(json_buf, sizeof(json_buf),
                    "{\"c\":%d,\"t\":%d,\"h\":%d}",
                    co2.val1,
                    temp.val1,
                    humi.val1
                );
                if (json_len < 0 || json_len >= sizeof(json_buf)) {
                    printk("SCD41 JSON overflow (%d bytes)\n", json_len);
                    snprintf(json_buf, sizeof(json_buf), "{\"error\":\"SCD41 JSON too large\"}");
                }
            }
            coap_send_data_request(json_buf);
        }

        // Handle CCS811
        if (ccs811_ready) {
            err = sensor_sample_fetch(ccs811);
            if (!err) err = sensor_channel_get(ccs811, SENSOR_CHAN_CO2, &eco2);
            if (!err) err = sensor_channel_get(ccs811, SENSOR_CHAN_VOC, &tvoc);

            if (err) {
                printk("CCS811 error: %d\n", err);
                snprintf(json_buf, sizeof(json_buf), "{\"error\": \"CCS811 read failed: %d\"}", err);
            } else {
				// For TVOC (parts per billion), show 2 decimals
				int tvoc_fraction = tvoc.val2 / 10000;	

                json_len = snprintf(json_buf, sizeof(json_buf),
                    "{\"ec\":%d,\"tv\":\"%d.%02d\"}",
                    eco2.val1, 
                    tvoc.val1, tvoc_fraction
                );
                if (json_len < 0 || json_len >= sizeof(json_buf)) {
                    printk("CCS811 JSON overflow (%d bytes)\n", json_len);
                    snprintf(json_buf, sizeof(json_buf), "{\"error\":\"CCS811 JSON too large\"}");
                }
            }
            coap_send_data_request(json_buf);
        }

        // Handle SPS30
        if (sps30_ready) {
            err = sensor_sample_fetch(sps30);
            if (!err) err = sensor_channel_get(sps30, SENSOR_CHAN_PM_2_5, &pm_2p5);
            if (!err) err = sensor_channel_get(sps30, SENSOR_CHAN_PM_10, &pm_10p0);

            if (err) {
                printk("SPS30 error: %d\n", err);
                snprintf(json_buf, sizeof(json_buf), "{\"error\": \"SPS30 read failed: %d\"}", err);
            } else {
				// PM2.5 and PM10: print fractional values with 2 decimal places
				int pm25_fraction = pm_2p5.val2 / 10000;  // val2 in micro units, so /10000 = 2 decimals
				int pm10_fraction = pm_10p0.val2 / 10000;

                json_len = snprintf(json_buf, sizeof(json_buf),
                    "{\"pm25\":\"%d.%02d\",\"pm10\":\"%d.%02d\"}",
                    pm_2p5.val1, pm25_fraction,
                    pm_10p0.val1, pm10_fraction
                );
                if (json_len < 0 || json_len >= sizeof(json_buf)) {
                    printk("SPS30 JSON overflow (%d bytes)\n", json_len);
                    snprintf(json_buf, sizeof(json_buf), "{\"error\":\"SPS30 JSON too large\"}");
                }
            }
            coap_send_data_request(json_buf);
        }

        // Sleep before next round
        k_msleep(SLEEP_TIME_MS);
    }
}

void coap_init(void)
{
    otInstance *instance = openthread_get_default_instance();
    otError error = otCoapStart(instance, OT_DEFAULT_COAP_PORT);
    if (error != OT_ERROR_NONE) {
        printk("Failed to start CoAP: %d\n", error);
    } else {
        printk("CoAP started on port %d\n", OT_DEFAULT_COAP_PORT);
    }
}
 
static void coap_send_data_response_cb(void * p_context, otMessage * p_message, const otMessageInfo * p_message_info, otError result){ 
  if (result == OT_ERROR_NONE) { 
    printk("Delivery confirmed.\n"); 
  } else { 
    printk("Delivery not confirmed: %d\n", result); 
  } 
} 

static void coap_send_data_request(char * data){ 
  otError       error = OT_ERROR_NONE; 
  otMessage   * myMessage; 
  otMessageInfo myMessageInfo; 
  otInstance  * myInstance = openthread_get_default_instance(); 
  const otMeshLocalPrefix *ml_prefix = otThreadGetMeshLocalPrefix(myInstance); 
  uint8_t serverInterfaceID[8]= {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01}; 
  
  do{ 
    myMessage = otCoapNewMessage(myInstance, NULL); 
    if (myMessage == NULL) { 
      printk("Failed to allocate message for CoAP Request\n"); return; 
    } 
  
    otCoapMessageInit(myMessage, OT_COAP_TYPE_CONFIRMABLE, OT_COAP_CODE_PUT); 
  
    error = otCoapMessageAppendUriPathOptions(myMessage, "storedata"); 
    if (error != OT_ERROR_NONE){ break; } 
  
    error = otCoapMessageAppendContentFormatOption(myMessage,  
                                        OT_COAP_OPTION_CONTENT_FORMAT_JSON ); 
    if (error != OT_ERROR_NONE){ break; } 
  
    error = otCoapMessageSetPayloadMarker(myMessage); 
    if (error != OT_ERROR_NONE){ break; } 
  
    error = otMessageAppend(myMessage, data, strlen(data)); 
    if (error != OT_ERROR_NONE){ break; } 

    memset(&myMessageInfo, 0, sizeof(myMessageInfo)); 
    memcpy(&myMessageInfo.mPeerAddr.mFields.m8[0], ml_prefix, 8); 
    memcpy(&myMessageInfo.mPeerAddr.mFields.m8[8], serverInterfaceID, 8); 
    myMessageInfo.mPeerPort = OT_DEFAULT_COAP_PORT; 
 
    error = otCoapSendRequest(myInstance, myMessage, &myMessageInfo, coap_send_data_response_cb, NULL); 
  }while(false); 
  
  if (error != OT_ERROR_NONE) { 
    printk("Failed to send CoAP Request: %d\n", error); 
    otMessageFree(myMessage); 
  }else{ 
    printk("CoAP data send.\n"); 
  } 
} 
