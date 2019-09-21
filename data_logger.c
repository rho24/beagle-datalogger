
#define __STDC_FORMAT_MACROS
#include <inttypes.h>

#include <stdio.h>
#include <signal.h>
#include <getopt.h>
#include <rc/mpu.h>
#include <rc/time.h>

// bus for Robotics Cape and BeagleboneBlue is 2
// change this for your platform
#define I2C_BUS 2

static int running = 0;
static uint64_t now, pastNow = 0;

// interrupt handler to catch ctrl-c
static void __signal_handler(__attribute__ ((unused)) int dummy)
{
	running=0;
	return;
}

int main()
{
	rc_mpu_data_t data; //struct to hold new data

	// set signal handler so the loop can exit cleanly
	signal(SIGINT, __signal_handler);
	running = 1;

	// use defaults for now, except also enable magnetometer.
	rc_mpu_config_t conf = rc_mpu_default_config();
	conf.i2c_bus = I2C_BUS;
	conf.enable_magnetometer = 1;
	conf.dmp_fetch_accel_gyro = 1;
	conf.show_warnings = 0;

	if(rc_mpu_initialize(&data, conf)){
		fprintf(stderr,"rc_mpu_initialize_failed\n");
		return -1;
	}

	if(rc_mpu_read_mag(&data)<0){
		printf("read mag data failed\n");
	}
	
	printf("starting\n");
	fflush(stdout);
	
	//now just wait, print_data will run
	while (running) {
		// read sensor data
		if(rc_mpu_read_accel(&data)<0){
			printf("read accel data failed\n");
		}
		if(rc_mpu_read_gyro(&data)<0){
			printf("read gyro data failed\n");
		}
		if(rc_mpu_read_mag(&data)<0){
			printf("read mag data failed\n");
		}

		pastNow = now;
		now = rc_nanos_since_boot();
		printf("%" PRIu64, now - pastNow);

		printf(",%06d,%06d,%06d,",\
						data.raw_accel[0],\
						data.raw_accel[1],\
						data.raw_accel[2]);
		printf("%06d,%06d,%06d,",\
						data.raw_gyro[0],\
						data.raw_gyro[1],\
						data.raw_gyro[2]);
		printf("%07.2f,%07.2f,%07.2f\n",\
						data.mag[0],\
						data.mag[1],\
						data.mag[2]);
		fflush(stdout);
		rc_usleep(100000);
	}

	rc_mpu_power_off();
	return 0;
}

