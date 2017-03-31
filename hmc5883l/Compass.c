#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <linux/i2c-dev.h>

#include <math.h>

#define HMC5883L_I2C_ADDR 0x1e

void selectDevice(int fd, int addr, char * name)
{
   if (ioctl(fd, I2C_SLAVE, addr) < 0)
   {
      fprintf(stderr, "%s not present\n", name);
      //exit(1);
   }
}

void writeToDevice(int fd, int reg, int val)
{
   char buf[2];
   buf[0]=reg; buf[1]=val;
   if (write(fd, buf, 2) != 2)
   {
      fprintf(stderr, "Can't write to HMC5883L\n");
      //exit(1);
   }
}

int main(int argc, char **argv)
{
   int x, y, z;
   float head;
   int fd;
   int res;
   unsigned char buf[16];
   unsigned char cmd[16];

   if ((fd = open("/dev/i2c-1", O_RDWR)) < 0)
   {
      // Open port for reading and writing
      fprintf(stderr, "Failed to open i2c bus\n");
      exit(1);
   }
       
   /* initialise HMC5883L */

   selectDevice(fd, HMC5883L_I2C_ADDR, "HMC5883L");


   /* Set address pointer to ident register (10) */

   /* Device documentation says
      To move the address pointer to a random register location, first issue a write
      to that location with no data byte following the command.
   */

   cmd[0] = 10;
   res = write(fd, cmd, 1);
   if (res != 1) {
     printf("Failed to write address");
     exit(-1);
   }

   /* Read device ident back */
   res = read(fd, buf, 3);
   if (res != 3) {
     printf("Failed to read");
     exit(-1);
   }

   printf("%c %c %c\n", buf[0], buf[1], buf[2]);
   if (buf[0] != 'H' || buf[1] != '4' || buf[2] != '3') {
     printf("Incorrect device id\n");
     exit(-1);
   }
   return 0;
}
