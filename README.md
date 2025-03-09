# Weaving Structure Installation Optimization
**Author:** Chia Hui Yen  
**Mentor:** Professor Huang Weixin  
**Coordinator:** Mr. Wei from Hebei Lu Cheng Machinery Co.  
**Date:** 2024 Spring  
**Files:** 
1. grasshopper files do simulations for data collection
2. Python-based analysis optimizer, processes simulation data to determine the optimal assembly sequence that minimizes displacements and ensures stability
3. Support machine design drawing and C++ hardware control program to transmit signal data between electronic components

## About the Project
This project began with my participation in Prof. Huang Weixin’s research group, where I explored weaving structures—a lightweight, customizable structural system.

More details on weaving structures can be found in the following research paper:
> Huang, W., Wu, C., Hu, J., & Gao, W. (2022). Weaving structure: A bending-active gridshell for freeform fabrication. Automation in Construction, 136, 104184.

Initially, I conducted design optimization using a genetic algorithm (<a href="https://hychia88.github.io/assets/pdfs/Networks.pdf" target="_blank">View Project</a>) and participated in several digital fabrication projects in Shenzhen and Beijing, China, as shown in the images below.

During the Beijing project, I gained hands-on experience in the challenges of customizing fabrication for weaving structures. In Shenzhen, I worked with irregular bending-active structures, where I observed how improper assembly sequences could lead to significant instability. As part of this project, I contributed to the automation pipeline and integrated a water system into the installation (<a href="https://hychia88.github.io/assets/pdfs/Droplet.pdf" target="_blank">Shenzhen Digital Fabrication Project Link↗</a>).

Through these experiences, I encountered multiple challenges in previous installation projects, which motivated me to further develop this research project and create an installation aid system.

Below is the **entire project development process**. Additionally, this repository contains the code for a Label Machine Control App, developed as part of the **Digital-Aided Installation and Optimization for Weaving Structures research project**. The system automates the labelling of round or rectangular rods (3mm–20mm) with customized codes at specific distances (defined via CSV input), significantly improving the efficiency of weaving structure installation. It was successfully implemented in a project in Bali, Indonesia, **where it improved installation efficiency by 33%.**

The system transforms the previously manual task of rod labelling into an automated process, significantly improving the assembly of bending-active gridshell structures. This enhancement provides:
- Automated labelling process
- Improved installation accuracy
- Increased assembly speed
- Reduced human error

</br>
<p align="center">
<img src="https://github.com/user-attachments/assets/02b4bc96-e3de-4e11-8339-9bc1c4ed72f8" alt="Weaving Structure Example" width="600"/>
<img src="https://github.com/user-attachments/assets/92a2786a-2804-45dd-9c4b-10282c22f4ce" width="600"/>
</p>

- **Challenge (1): Unstable shape during installation**
<p align="center">
<img src="https://github.com/user-attachments/assets/e61ee5f0-ae94-47bc-b98b-6d64b8159844" width="800"/>
</p>

- **Challenge (2): Irregular connecting points lead to massive amount of manual labelling work**
<p align="center">
<img src="https://github.com/user-attachments/assets/98342d23-9ebe-4fa8-aee8-b60b8af6780e" width="800"/>
</p>  

## Optimization (1): Optimization of the installation sequences 
### (1) Simulate the Installation Process:
Run massive simulations to track how structures move and change during installation. Collect displacement data for further analysis. Pipeline built in grsshopper, rhino and kangaroo.
![image](https://github.com/user-attachments/assets/a81525ca-91e8-43f2-b83a-287e1f0bd709)
![image](https://github.com/user-attachments/assets/6197931a-54d7-44e3-aabd-e488dbe618e2)

### (2) Analysis of Sequence & Rod Performance
Compare changes in sequence and displacement to understand the basic rules of the process.  
Can be check at the file: <a href ="Installation Sequences Optimization\seq_analysis.py"> seq_analysis.py </a>
- tags_data: Dictionary containing different assembly sequences, where each sequence lists the rods in the order they are assembled.
- data: Corresponding displacement values for each sequence, recording the maximum displacement at each step.
- built_values: A predefined score for each rod indicating its ease of construction, comprehensively considering rod length, shape complexity, and number of nodes.

#### Result:
**Multiple analyses:** metric comparisons, influence factors by different metrics, final influence vs. built values, top sequence displacement curves, and optimal assembly sequence visualization.
<p align="center">
<img src="analysis_result_S3\comprehensive_analysis.png" alt="comprehensive_analysis" width="800"/>
</p>

**"Metrics Comparison:** Four scatter plots showing relationships between different metrics (maximum, range, and average displacement) and a histogram of combined metric values, demonstrating how these metrics correlate.
<p align="center">
<img src="analysis_result_S3/metrics_comparison.png" alt="Metrics Comparison" width="800"/>
</p>

**Recommended assembly sequence:** The top panel shows rods ranked by influence factor, while the bottom panel displays control values across assembly steps.
<p align="center">
<img src="analysis_result_S3\optimal_sequence.png" alt="optimal_sequence" width="800"/>
</p>

#### Validation： 
As the result shown above the predicted best sequences is **PREDICT = [#2, #4, #3, #0, #1, #8, #5, #7, #14, #9, #6, #10, #13, #11, #15, #12]**

Compare the sequence to the previous sequence we can see it's satable, effective, converge than avergae. Proven is a workable algorithm.


### (3) Generate Installation Guidelines:
Use these rules to create helpful installation sequences for workers. Below are some sample cases.
![re](https://github.com/user-attachments/assets/0d3591bd-e69c-4119-9ff3-c91725ae4cb9)
![re2](https://github.com/user-attachments/assets/8e3dc30a-0cfa-4555-93ca-3f177dcc7614)


## Optimization (2): Development of an automatic rod marking system.  
### **Design Draft**
<div>
    <img src="https://github.com/user-attachments/assets/22eb9002-d08d-4fe4-802f-878a4dc6f411" alt="Machine Design Draft" width="40%" style="float: left"/>
    <img src="https://github.com/user-attachments/assets/86c00e8c-e232-4e80-88c8-eaedc4079a56" alt="process" width="60%" style="float: left"/>
</div>  

### Final Machine
<img src="https://github.com/user-attachments/assets/bfffeed1-4324-43eb-ad15-ed9dee3c3e99" alt="Final Machine"/>


## Result Improvement
This application supports custom-designed hardware for automatic rod marking, enabling precise, random-position labelling on weaving rods. The system specifically addresses challenges in manual rod marking for bending-active grid shell structures.  

- **Installation Efficiency**: 33% reduced installation time through an improved rod labelling process, enhancing overall efficiency for weaving structure fabrication
- **Enhanced User Experience**: Improved label design with color-coded system for easier rod identification and assembly

### Rod Specifications
<img src="https://github.com/user-attachments/assets/3492cd20-0831-4f46-89f5-f3aa6bb9e6e2" alt="Rod Section" width="400"/>


### Label Design
<img src="https://github.com/user-attachments/assets/b7f1adda-6612-48db-b894-be40f55b5e41" alt="Label Design 1" width="400"/>
<img src="https://github.com/user-attachments/assets/cc4e3a9f-e56c-49d6-84d6-469e8ff6a964" alt="Label Design 2" width="400"/>

### Key Features
- **Precise Labeling:** Millimeter-level precision marking
- **Customizable Positions:** Random distance printing based on project requirements
- **Multi-Color Printing System:**
  - Red: Codes ending in 0-3
  - Blue: Codes ending in 4-6
  - Green: Codes ending in 7-9
- **Versatile Rod Support:** Compatible with various cross-sections (3mm-20mm)
- **CSV Integration:** Automated processing of labeling instructions

<img src="https://github.com/user-attachments/assets/0623a1ea-77a6-4372-9be9-f6a77336d4f6" alt="Final Result" />
