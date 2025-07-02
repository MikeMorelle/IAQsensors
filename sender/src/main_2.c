
/* CO2 Sensor SCD41
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/device.h>
#include <zephyr/logging/log.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/drivers/sensor/ccs811.h>

#include "sensor/scd4x/scd4x.h"


#if !DT_HAS_COMPAT_STATUS_OKAY(sensirion_scd41)
#error "No sensirion,scd4x compatible node found in the device tree"
#endif



const struct device *scd41 = DEVICE_DT_GET_ANY(sensirion_scd41);
const struct device *ccs811 = DEVICE_DT_GET_ANY(ams_ccs811);


int main (void){
       
        if (!device_is_ready(scd41)) {
                printk("SCD41 device is not ready\n");
                return 1;
        }
        if (!device_is_ready(ccs811)) {
        printk("CCS811 device is not ready\n");
        return 1;
    }
    
        struct sensor_value co2, temo, humi;
        struct sensor_value eco2, tvoc;
        while(true){

                sensor_sample_fetch(scd41);
                sensor_channel_get(scd41, SENSOR_CHAN_CO2, &co2);
                sensor_channel_get(scd41, SENSOR_CHAN_AMBIENT_TEMP, &temo);
                sensor_channel_get(scd41, SENSOR_CHAN_HUMIDITY, &humi);
                printk("CO2: %d.%06d ppm, Temperature: %d.%06d C, Humidity: %d.%06d %%\n",
                       co2.val1, co2.val2, temo.val1, temo.val2, humi.val1, humi.val2);

                int ret = sensor_sample_fetch(ccs811);
                if (ret) {
                    printk("Failed to fetch CCS811 sensor data: %d\n", ret);
                    k_sleep(K_SECONDS(5));
                    continue;
                }

                ret = sensor_channel_get(ccs811, SENSOR_CHAN_CO2, &eco2);
                if (ret) {
                    printk("Failed to get eCO2 data: %d\n", ret);
                }

                ret = sensor_channel_get(ccs811, SENSOR_CHAN_VOC, &tvoc);
                if (ret) {
                    printk("Failed to get TVOC data: %d\n", ret);
                }

                printk("eCO2: %d ppm, TVOC: %d ppb\n", eco2.val1, tvoc.val1);

                k_sleep(K_SECONDS(10));
        }
        return 0;
}
*/



/*
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/drivers/sensor/ccs811.h>


const struct device *ccs811 = DEVICE_DT_GET_ANY(ams_ccs811);

int main(void)
{
    if (!device_is_ready(ccs811)) {
        printk("CCS811 device is not ready\n");
        return 1;
    }
    printk("CCS811 device is ready\n");
    

    struct sensor_value eco2, tvoc;

    while (true) {
        int ret = sensor_sample_fetch(ccs811);
        if (ret) {
            printk("Failed to fetch CCS811 sensor data: %d\n", ret);
            k_sleep(K_SECONDS(5));
            continue;
        }

        ret = sensor_channel_get(ccs811, SENSOR_CHAN_CO2, &eco2);
        if (ret) {
            printk("Failed to get eCO2 data: %d\n", ret);
        }

        ret = sensor_channel_get(ccs811, SENSOR_CHAN_VOC, &tvoc);
        if (ret) {
            printk("Failed to get TVOC data: %d\n", ret);
        }

        printk("eCO2: %d ppm, TVOC: %d ppb\n", eco2.val1, tvoc.val1);

        k_sleep(K_SECONDS(10));
    }

    return 0;
}
*/

#include <stdio.h> 
#include <zephyr/devicetree.h> 
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/device.h>
#include <zephyr/logging/log.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/drivers/i2c.h>
#include "sensor/sps30/sps30.h"
#include "sensor/sps30/sensirion_i2c.h"

#define I2C_DEV_NAME "I2C_1"

void print_measurement_data(struct sps30_measurement *measurement) {
    printf("1.0um concentration: %.2f µg/m³\n", measurement->mc_1p0);
    printf("2.5um concentration: %.2f µg/m³\n", measurement->mc_2p5);
    printf("4.0um concentration: %.2f µg/m³\n", measurement->mc_4p0);
    printf("10.0um concentration: %.2f µg/m³\n", measurement->mc_10p0);
    printf("Typical particle size: %.2f µm\n", measurement->typical_particle_size);
}

int main(void) {
    struct sps30_measurement m;
    int16_t ret;

    // Initialize I2C bus
    sensirion_i2c_init();

    // Create a dev_bus structure for the I2C communication
    struct i2c_dt_spec dev_bus = {
        .bus = device_get_binding(I2C_DEV_NAME),
        .addr = 0x69  // I2C address of the SPS30 sensor
    };
    printk("Using I2C device: %s\n", dev_bus.bus->name);
    // print full dev_bus structure
    printf("I2C Device: %s, Address: 0x%02X\n", dev_bus.bus->name, dev_bus.addr);
    if (!device_is_ready(dev_bus.bus)) {
        printf("I2C device is not ready\n");
        return -1;
    }

    // Busy loop for initialization, keep probing the sensor until it's ready
    while (sps30_probe(&dev_bus) != 0) {
        printf("SPS sensor probing failed\n");
        sensirion_sleep_usec(1000000);  // Wait 1s before retrying
    }
    printf("SPS sensor probing successful\n");

    // Read and print the firmware version
    uint8_t fw_major, fw_minor;
    ret = sps30_read_firmware_version(&dev_bus, &fw_major, &fw_minor);
    if (ret) {
        printf("Error reading firmware version\n");
    } else {
        printf("FW: %u.%u\n", fw_major, fw_minor);
    }

    // Read and print the serial number
    char serial_number[SPS30_MAX_SERIAL_LEN];
    ret = sps30_get_serial(&dev_bus, serial_number);
    if (ret) {
        printf("Error reading serial number\n");
    } else {
        printf("Serial Number: %s\n", serial_number);
    }

    // Start the measurement
    ret = sps30_start_measurement(&dev_bus);
    if (ret < 0) {
        printf("Error starting measurement\n");
    } else {
        printf("Measurements started\n");
    }

    // Main loop to continuously read and print measurements
    while (1) {
        sensirion_sleep_usec(SPS30_MEASUREMENT_DURATION_USEC);  // Wait for 1 second
        ret = sps30_read_measurement(&dev_bus, &m);
        if (ret < 0) {
            printf("Error reading measurement\n");
        } else {
            print_measurement_data(&m);
        }
    }

    return 0;
}

