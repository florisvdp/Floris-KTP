# Overview
This is the code for our orthopedic triage project, where a doctor can decide on the best medical intervention based on patient data. Run main.py to start the triage procedure. 
Explanation of files: 
. orthopedic_rules_2.json: JSON file that holds the rules/facts/conclusions from the knowledge system
. main.py: the main file to run the procedure
. inference_engine.py: holds the forward- and backward inference engine algorithms
. knowledg_base.py: holds the classes for the Rule and KnowledgeBase objects
. gui.py: holds the logic for our User Interface

# How to run

Ensure you have tkinter installed, then simply run `python main.py`.