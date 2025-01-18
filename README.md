# Weaving-Structure-Installation-Optimization-and-Automated
**Author:** Chia Hui Yen | 
**Mentor:** Professor Huang Weixin | 
**Coorditor:** Mr.Wei from Hebei Lu Cheng Machinery Co. | 
**Date:** 2024 Spring  

## About the project  
This library included the code of Label Machine Control App. This is part of the research project “Digital Aided Installation and Optimization for Weaving Structures”. The app controls an automatic rod marking system, designed to label round or rectangular rods (3mm–20mm) with customized codes at specific distances as defined in a pre-generated CSV file. This system streamlines the labeling process for weaving structures, significantly improving efficiency.  

### Preface  
- The actual project I previous participated, and found challendges in the installation workflow
![image](https://github.com/user-attachments/assets/92a2786a-2804-45dd-9c4b-10282c22f4ce)
![image](https://github.com/user-attachments/assets/eab4bb4a-7ed3-45af-b95c-a84d4188b5e8)
- An example of weaving structure:  
![image](https://github.com/user-attachments/assets/02b4bc96-e3de-4e11-8339-9bc1c4ed72f8)

- The design draft of the machine:  
![image](https://github.com/user-attachments/assets/22eb9002-d08d-4fe4-802f-878a4dc6f411)  

- The machine developed in the end:
![image](https://github.com/user-attachments/assets/bfffeed1-4324-43eb-ad15-ed9dee3c3e99)


## Description:
This app supports the hardware I designed for automatic rod marking. The hardware enables precise, random-position labeling on weaving rods, addressing challenges in manual rod marking for bending-active gridshell structures.  

The system has improved the rod installation process by approximately 33% compared to manual methods. It enhances accuracy and efficiency, especially in projects requiring high customization, such as those described in Huang, W., Wu, C., Hu, J., & Gao, W. (2022). Weaving structure: A bending-active gridshell for freeform fabrication (DOI: 10.1016/j.autcon.2022.104184).  

## Features:  
- The section of weaving structure rod:
![image](https://github.com/user-attachments/assets/3492cd20-0831-4f46-89f5-f3aa6bb9e6e2)

- The design of the label

![image](https://github.com/user-attachments/assets/b7f1adda-6612-48db-b894-be40f55b5e41)
![image](https://github.com/user-attachments/assets/cc4e3a9f-e56c-49d6-84d6-469e8ff6a964)

- Precise Labeling: Marks rods with millimeter-level precision.
- Customizable Positions: Prints labels at random distances based on project-specific requirements.
- Multi-Colour Printing: The system dynamically selects the ink colour based on the last digit of the number code. For example:
    Codes ending in 0–3 are printed in Red.
    Codes ending in 4–6 are printed in Blue.
    Codes ending in 7–9 are printed in Green.
- Supports Various Rod Types: Works with rods of different cross-sections and diameters (3mm–20mm).
- CSV Integration: Automatically processes labeling instructions from a CSV file.  


The final result of the machine:
![image](https://github.com/user-attachments/assets/0623a1ea-77a6-4372-9be9-f6a77336d4f6)


## Application:
The labeled rods simplify the assembly process for bending-active gridshell structures. Previously a manual task, labeling is now automated, enhancing speed and accuracy. Below are examples of real-world projects where this system was applied.
