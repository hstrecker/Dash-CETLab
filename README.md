# Dash-CETLab
Dash plotly module to accompany research from UCSB CETLab website (Optimal Energy Pathways for Southern Africa)
 
> Author: Henry Strecker <br>
> Date: March 2023

This readme outlines all of the intricacies that went into creating the module that is deployed to the UCSB CETLab website: https://cetlab.es.ucsb.edu/projects/optimal-energy-pathways

Data:<br> All of the data used for plotting is located in the ModuleData folder. All of the files are of form *.csv and were generated from a number of different jupyter notebooks that were sourced from the project github page. Note that all of these dataframes should be unedited from their original state when saved from the notebooks. All of the notebooks can be found under this directory: https://github.com/cetlab-ucsb/southern_africa_electricity/tree/master/gridpath/results_analysis_scripts

Future New Capacity and Cost Tab Data:
- Bar plots: df_pt_all_cap_tech_allscs and df_pt_gen_loss_curt_allscs from plot_newcap_genmix_all_periods_kc.ipynb
- Line plots: costs_to_plot and emissions_to_plot dataframes from plot_cost_emissions_all_periods.ipynb

Country New-Build Capacity Tab Data:
- df_nbuilt_hydro, df_nbuilt_vre, and df_nbuilt_fossil dataframes from plot_newcap_by_countries.ipynb

Transmission Capacities Tab Data:
- df_trans_newcap_lz_40_allscs_latlon from plot_trans_newcap.ipynb

Dash.py:<br>This python file contains the code that generates the module you see on the website. The document is commented with labels for various components which I will reference here. I will go much more in depth in this document in hopes that anyone else can make updates or changes.

## Imports and Global Variables
Imports: Import necessary packages

Import Existing Data: load csv files from ModuleData folder

Colors: Set color scheme for different energy types

Checklist options: Creates a list of scenarios that will be later passed into a dash checklist. In the event that more scenarios are generated, these scenario names should be added to the list, and their data appended to the appropriate existing csv files. It is important that the string added into this list is exactly the same as how it appears in the data.

Data transformation for country bar plots: Merges the three distinct dataframes together, and renames some values so that they are consistent with the rest of the file.

Dictionary for transmission maps: This will be used as a way to link together transmissions of the same magnitude with the right name and width in the maps on tab 4.

Data transformation for transmission maps: Generates a column for each scenario that records the magnitude range each individual transmission falls into.

## Dash Application Layout
This defines the format of the dash module and the content within it. It uses a combination of Dash Bootstrap Components (dbc), Dash Core Components (dcc), and html components. DBC like Container and Row define the more rigid structure of the module, they act as the containers for the more intricate components. DCC like Tabs, Checklist, and Graph are the interactive components of the module that create the Dash user experience. Html like P, Center, and Div are html components that can be used in dash to display text and format components on a smaller scale. Now that we have talked about the main types of components, I will explain how they all come together to create the module.

The entire module is wrapped within a dbc.Container component
The outermost layer is dcc.Tabs, which allows you to make tabs that can be toggled between.
Inside that are dcc.Tab components, each of which defines a specific tab and its contents.

### Tabs

- Overview Tab 
Includes a few html components that display text to explain how the module works to the user.

- Future New Capacity and Cost Tab 
Contains an html.P component for the scenario selection text. Then there is a dcc.Checklist, where the options are set to be checklist_options as defined above. In that chunk we also set the id value for the checklist and apply formatting. Next we have a series of dcc.Graph components that are wrapped in html.Center. This is done so that all of the figures are centered on the page. Note how the graphs themselves are not defined in this section, they simply have an id assigned to them. We can do this because we will later assign the plots to their respective id using Dash callbacks.

- Country New-Build Capacity Tab
Follows a similar structure to the one above, with the same default checklist, and a single centered plot.

- Transmission Capacities Tab 
Has the same structure as the prior two, but there is one plot that is composed of multiple subplots, based on what scenarios are selected from the checklist.

### Dash Application Callbacks 
Here is a link to the documentation on it: https://dash.plotly.com/basic-callbacks
These code chunks allow us to take user inputs and use them to redefine other aspects of the module, like graphs. They begin with the general call `@app.callback(Output(id, type), Input(id, type))` followed by a function definition. The input should come from a dcc component in the module, and the return value of the function will be sent to the output dcc component. In order for the input and output to correctly map to their desired dcc components, we must match the ids with how they were defined in the dash layout. This process may become more clear with the example in the documentation linked above. 

1. Callback1 - Synchronize Checklists across multiple tabs<br>
This is maybe the most confusing callback, because the inputs and outputs are the same objects. This is because we want to keep the three checklist synchronized. Thus we have defined them all to be inputs, check which one has been altered, and update the other two accordingly.

2. Callback2 - Create all plots in the 'Future New Capacity and Cost' tab <br>
This takes the tab2 checklist as input (which is a list), uses the checklist to filter the data accordingly, and generates the plots using the existing code from the same jupyter notebooks where the data was generated from. Notice here how there are three different figures defined throughout the function (fig1, fig2, and fig3), and they are all returned in the order that the outputs are listed in the @app.callback portion of the code.

3. Callback3 - Create the singular plot for the 'Country New-Build Capacity' tab<br>
Follows from the same general structure of Callback2. The code to make the plot was heavily altered from the notebook it originated from, so that I could show all of the countries at once.

1. Callback4 - Create the singular plot for the 'Country New-Build Capacity' tab<br>
This callback uses the checklist as an input to determine which scenarios to plot. The code for these plots are entirely new, meaning it won't be found in any of the project notebooks. The checklist is used to generate the correct number of subplots, with for loops iterating through each scenario and plotting each transmission value to its corresponding subplot. The use of dummy markers allows the user to toggle on and off the transmission magnitude categories.


The last bit of code beyond the callbacks allows the module to be deployed locally when the python file is run.

