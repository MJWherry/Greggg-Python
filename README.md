# Greggg-Python
<p>The code in this repo is developed for the docent-robot project
currently in development at Slippery Rock University. The robot 
(known as Greggg) requires custom software to be written to control
the low level hardware. The components are connected to a Raspberry Pi
3 Model B and are listed below:</p>
<ul>
<li>DHB-10 Motor Control Board</li>
<li>Ping))) Sonar sensors</li>
<li>uBlox GPS Module</li>
<li>Triple-axis Magnetometer (Compass) Board - HMC5883L</li>
</ul>
<p>The main driver is written in python and calls several other classes,
each one will handle a specific hardware component</li>
