///////////////////////////////////////////////////////////
// BIBLIOTECAS A INSTALAR EN ARDUINO IDE
// - Grove Ultrasonic Ranger
// - Grove IMU 9DOF 9250 (Yo no lo encontré en la biblioteca de Arduino)
///////////////////////////////////////////////////////////

// define ultrasonic ranger data pin
#include "Ultrasonic.h"  // include Seeed Studio ultrasonic ranger library
#define RANGERPIN 8

#include "Wire.h"

// I2Cdev and MPU6050 must be installed as libraries, or else the .cpp/.h files
// for both classes must be in the include path of your project
#include "I2Cdev.h"
#include "MPU9250.h"

#define sample_num_mdate  2500  // para la calibracion

////////////////////////////////////////////////////////////

Ultrasonic ultrasonic(RANGERPIN); // initialize ultrasonic library

// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU9250 accelgyro;
I2Cdev   I2C_M;


uint8_t buffer_m[6];

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t mx, my, mz;

float heading;
float tiltheading;

float Axyz[3];
float Gxyz[3];
float Mxyz[3];

volatile float mx_sample[3];
volatile float my_sample[3];
volatile float mz_sample[3];

static float mx_centre = 0;
static float my_centre = 0;
static float mz_centre = 0;

volatile int mx_max = 0;
volatile int my_max = 0;
volatile int mz_max = 0;

volatile int mx_min = 0;
volatile int my_min = 0;
volatile int mz_min = 0;

 
void setup(){

  // join I2C bus (I2Cdev library doesn't do this automatically)
  Wire.begin();

  // Iniciamos el monitor serie para mostrar el resultado (para ver resultados: tools -> serial monitor)
  //Serial.begin(38400);
  Serial.begin(9600);

  // initialize device
  while(!Serial);
  
  //Initializing I2C devices...
  accelgyro.initialize();

  // verify connection
  //Testing device connections...
  //Serial.println(accelgyro.testConnection() ? "MPU9250 connection successful" : "MPU9250 connection failed");

  Mxyz_init_calibrated();

  delay(1000);
}


void loop(){

  // SENSOR ULTRASONICO //////////////////////////////////////////
  int centimeters;
  centimeters = ultrasonic.MeasureInCentimeters();  // centimeters

  //Serial.print("1-");
  //Serial.println(centimeters);

  //delay(150);

  // SENSOR ACELEROMETRO //////////////////////////////////////////
  getAccel_Data();
  getGyro_Data();
  getCompassDate_calibrated(); //compass data has been calibrated here
  getHeading();                // before we use this function we should run 'getCompassDate_calibrated()' first, so that we can get calibrated data ,then we can get correct angle .                    
  getTiltHeading(); 

  String info = String("1-")+centimeters+"|2.1-"+mx_centre+","+my_centre+","+mz_centre+"|2.2-"+Axyz[0]+","+Axyz[1]+","+Axyz[2]+"|2.3-"+Gxyz[0]+","+Gxyz[1]+","+Gxyz[2]+"|2.4-"+Mxyz[0]+","+Mxyz[1]+","+Mxyz[2];
  
  Serial.println(info);
  delay(100);
  Serial.flush();
  
  // Calibracion
  /*Serial.print("2.1-");
  Serial.print(mx_centre);
  Serial.print(",");
  Serial.print(my_centre);
  Serial.print(",");
  Serial.println(mz_centre);

  //Acceleration
  Serial.print("2.2-");
  Serial.print(Axyz[0]);
  Serial.print(",");
  Serial.print(Axyz[1]);
  Serial.print(",");
  Serial.println(Axyz[2]);

  //Gyro(degress/s)
  Serial.print("2.3-");
  Serial.print(Gxyz[0]);
  Serial.print(",");
  Serial.print(Gxyz[1]);
  Serial.print(",");
  Serial.println(Gxyz[2]);

  // Compass Value
  Serial.print("2.4-");
  Serial.print(Mxyz[0]);
  Serial.print(",");
  Serial.print(Mxyz[1]);
  Serial.print(",");
  Serial.println(Mxyz[2]);
  
  // The clockwise angle between the magnetic north and X-Axis
  Serial.print("2.5-");
  Serial.println(heading);

  //The clockwise angle between the magnetic north and the projection of the positive X-Axis in the horizontal plane
  Serial.print("2.6-");
  Serial.println(tiltheading);
  
  delay(150);*/
}


void getHeading(void) {
  heading=180*atan2(Mxyz[1],Mxyz[0])/PI;
  if(heading <0) heading +=360;
}

void getTiltHeading(void) {
  float pitch = asin(-Axyz[0]);
  float roll = asin(Axyz[1]/cos(pitch));

  float xh = Mxyz[0] * cos(pitch) + Mxyz[2] * sin(pitch);
  float yh = Mxyz[0] * sin(roll) * sin(pitch) + Mxyz[1] * cos(roll) - Mxyz[2] * sin(roll) * cos(pitch);
  float zh = -Mxyz[0] * cos(roll) * sin(pitch) + Mxyz[1] * sin(roll) + Mxyz[2] * cos(roll) * cos(pitch);
  tiltheading = 180 * atan2(yh, xh)/PI;
  if(yh<0)    tiltheading +=360;
}


void Mxyz_init_calibrated () {
  
  //Before using 9DOF,we need to calibrate the compass frist,It will takes about 2 minutes
  //During  calibratting ,you should rotate and turn the 9DOF all the time within 2 minutes
  //Serial.println(F("If you are ready ,please sent a command data 'ready' to start sample and calibrate."));
  //while(!Serial.find("ready")); 
  
  get_calibration_Data ();
  
  //Serial.println("compass calibration parameter ");
  //Serial.print(mx_centre);
  //Serial.print(my_centre);
  //Serial.println(mz_centre);
}

void get_calibration_Data () {
    for (int i=0; i<sample_num_mdate;i++){
      get_one_sample_date_mxyz();
      /*
      Serial.print(mx_sample[2]);
      Serial.print(" ");
      Serial.print(my_sample[2]);                            //you can see the sample data here .
      Serial.print(" ");
      Serial.println(mz_sample[2]);
      */
      
      if (mx_sample[2]>=mx_sample[1])mx_sample[1] = mx_sample[2];     
      if (my_sample[2]>=my_sample[1])my_sample[1] = my_sample[2]; //find max value      
      if (mz_sample[2]>=mz_sample[1])mz_sample[1] = mz_sample[2];   
      
      if (mx_sample[2]<=mx_sample[0])mx_sample[0] = mx_sample[2];
      if (my_sample[2]<=my_sample[0])my_sample[0] = my_sample[2];//find min value
      if (mz_sample[2]<=mz_sample[0])mz_sample[0] = mz_sample[2];
            
    }
      
      mx_max = mx_sample[1];
      my_max = my_sample[1];
      mz_max = mz_sample[1];      
          
      mx_min = mx_sample[0];
      my_min = my_sample[0];
      mz_min = mz_sample[0];
  
      mx_centre = (mx_max + mx_min)/2;
      my_centre = (my_max + my_min)/2;
      mz_centre = (mz_max + mz_min)/2;  
}


void get_one_sample_date_mxyz(){   
    getCompass_Data();
    mx_sample[2] = Mxyz[0];
    my_sample[2] = Mxyz[1];
    mz_sample[2] = Mxyz[2];
} 


void getAccel_Data(void){
  accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
  Axyz[0] = (double) ax / 16384;//16384  LSB/g
  Axyz[1] = (double) ay / 16384;
  Axyz[2] = (double) az / 16384; 
}

void getGyro_Data(void){
  accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
  Gxyz[0] = (double) gx * 250 / 32768;//131 LSB(��/s)
  Gxyz[1] = (double) gy * 250 / 32768;
  Gxyz[2] = (double) gz * 250 / 32768;
}

void getCompass_Data(void){
  I2C_M.writeByte(MPU9150_RA_MAG_ADDRESS, 0x0A, 0x01); //enable the magnetometer
  delay(10);
  I2C_M.readBytes(MPU9150_RA_MAG_ADDRESS, MPU9150_RA_MAG_XOUT_L, 6, buffer_m);
  
  mx = ((int16_t)(buffer_m[1]) << 8) | buffer_m[0] ;
  my = ((int16_t)(buffer_m[3]) << 8) | buffer_m[2] ;
  mz = ((int16_t)(buffer_m[5]) << 8) | buffer_m[4] ;  
  
  //Mxyz[0] = (double) mx * 1200 / 4096;
  //Mxyz[1] = (double) my * 1200 / 4096;
  //Mxyz[2] = (double) mz * 1200 / 4096;
  Mxyz[0] = (double) mx * 4800 / 8192;
  Mxyz[1] = (double) my * 4800 / 8192;
  Mxyz[2] = (double) mz * 4800 / 8192;
}

void getCompassDate_calibrated (){
  getCompass_Data();
  Mxyz[0] = Mxyz[0] - mx_centre;
  Mxyz[1] = Mxyz[1] - my_centre;
  Mxyz[2] = Mxyz[2] - mz_centre;  
}
