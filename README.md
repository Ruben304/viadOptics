# VIAD Optics
*Visually Impaired Assistive Device* - for anyone who needs it 
## Collaborators 
- Jose Battle
- Ruben F. Carbajal
- Leanorine Lorenzano
- Zachary Dion Tan
- Axel S. Toro Vega
## VIAD Mission & Solution
VIAD aims to eliminate the high barrier of help needed for these visually impaired individuals and assist them in their daily life. 

Our device harnesses the capabilities of LIDAR sensors and advanced machine learning algorithms to enhance object recognition, enabling us to identify potential threats to the user. This innovative system is driven by a versatile microprocessor, which can be powered either by a rechargeable battery for a full day's use or by easily replaceable batteries for added convenience. Our vision includes developing a user-friendly notification system that utilizes haptic feedback and sound alert
## Architecture 
![ArchitectureDiagram](images/ArchitectureDiagramV1E1.drawio.png)

## Software Used
- Luxonis API for creating the image capturing, creating a neural network, object recognition: [Here](https://github.com/luxonis/depthai)
  - Some of the Pre Build Code Samples that can prove useful to us are:
    - API Interoperability
    - Collision Avoidance
    - Speed Calculation 
    - Spatial Detection
    - Yolo SDK
    - Vehicle Detection
    - Custom Trigger 
    - Custom Trigger Action
    - All the ones above can be found [Here](https://docs.luxonis.com/projects/sdk/en/latest/tutorials/code_samples/#)
#### Helpful Repos to look into 
- depthai python api: [Here](https://github.com/luxonis/depthai-python)
- depthai experiments: [Here](https://github.com/luxonis/depthai-experiments)
- next steps: [Here](https://docs.luxonis.com/en/latest/pages/tutorials/first_steps/)
## Materials Used
- Luxonis OAK-D Pro W Camera & Sensors
- Raspberry Pi Zero 2 W
- Haptic Motor
- GoPro Batteries
- 3D Print frames & enclosure

