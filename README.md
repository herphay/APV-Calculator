# Actuarial Present Value Calculator by Lim Her Phay
#### Video Demo: 

## Project motivation
This project was ported over from a Google Sheets calculator I implemented previously for Actuarial Present Value (APV) calculations for personal insurance comparison purposes. The key problem faced by me, and I believe other consumers, is that we cannot properly value and compare between different life insurance policies. A common question is do you buy whole life insurance, or a term life that covers you up to a certain age? If you do buy term, to what age do you cover? These and other such questions plague us and insurance agents have no incentive to provide a clear answer, and at least in Singapore, they almost certainly have no training to provide a quantitative based answer.

This left individual research as the only option left. The most objective way to answer the above question is naturally how insurance companies themselves would value them. In comes the whole discipline of Actuarial Science, for those unfamiliar, this discipline uses math and statistics to quantify risks and mainly applies their expertise in the insurance industry. This is the foundation of insurance, which are fundamentally risk transfer instruments. To make money in the industry, accurate methodology to quantify and value the risks are then required.

The actuarial present value immediately pops up as **the** metric to value life insurance policies (and more generally life annuities). In essence, it calculates the expected value of a life policy based on a population's mortality statistics. Naturally, the next step is to implement a calculator to help value policies quantitatively using the actuarial present value.

This project aims to provide a more user friendly interface for APV calculation as a website as opposed to a spreedsheet, to complete the CS50x final project, and to practice my coding skills. Due to my focus, I treat the web-dev as a side story with heavy lifting done by CS50x finance pset template (for visual appeal).

## DISCLAIMER
I have no professional training in the Actuarial Sciences, all calculations are done based on my best understanding, use at your own risk.

## Project Breakdown
### Overview & Usage
The calculator is implemented as a website using flask in python for the backend, and simple HTML/Javascript for frontend. It is meant to be hosted locally, once installing all the requirements in requirements.txt, a user should run `python helpers.pu` to create the required sqlite3 database if they did not download it from the repository, then they can simply `flask run` and access the site and the calculator within. The required input data, which is a life table, has been provided within the repository as a csv file. The data is published by the Singapore Department of Statistics [here](https://www.singstat.gov.sg/publications/population/complete-life-table).

### The site structure
The site contains 4 pages.
- Summary: This page contains mainly word descriptions to explain what is the APV, and the usage guide for the site itself.
- APV Calculator: This page takes user input specifying the parameters for an insurance policy they are interested in, and the parameters used to calculate the APV and a detailed yearly breakdown. After each calculation, the user can choose to save the policy details for future comparison.
- Life Tables: For user to explore the different life tables available to be used as calculation input. Mortality trend can be observed here.
- Comparison: This page will display all stored user policies, and the total APV. A redirect link is available for users to checkout the yearly breakdown in the APV page for all their stored policies.

### File functionality
#### app.py
This file contains the main backend implementation for the site. It defines the route for all 4 pages described above and is designed to contain minimal calculations. All the detailed user input verification, APV calculations, database read/write etc. are imported from helpers.py to keep it clean and let it's focus be on webpage behavior. As a site, no responses or pages are cached to prevent users from seeing stale data.

A few key routes' implementation are described below:
1. APV Calculator page:
   - Pages accepts both GET and POST method to submit the parameters used for calculation
       - POST is used for new policy input, where users enter their specific policy's parameters into a form defined on the page
       - GET is used for 2 behaviors
           - Default: Renders the default page and ask for user input
           - Redirected: The comparison page allows users to seek the detailed yearly breakdown of their saved policy, clicking on the view button there will redirect users here with the detailed parameters pre-filled using GET and URL arguments. This is more elegant to implement rather than simulating a POST. All the detailed values will be recalculated as it does not require much compute. 
2. save_plan:
   - A virtual route that will be called on the APV calculator page. This route is called once the user verified their APV details and want to save the plan for detailed comparison. As such it only accepts the POST method. Once they click the save button. All relevant details of the plan will be passed to this route and attempt to be saved into the database

#### helpers.py
This file contains the detail implementation for all non-web specific functions. They are described below:
1. Main: This creates the required sqlite3 database and the required table within. Users need to have the lifetable data ready before running this.
2. get_available_years: This get all the years which we have life table data available from the databse
3. get_life_table: This helps to pull a specific year and sex's life table
4. calc_insurance_value: this is the APV's calculator function. It takes in a specific life table and all the other associated parameters to calculate the APV. An iteration method through each year of the life table is used as more powerful libraries such as pandas and numpy are deliberately avoided to challenge myself into using as little libraries as possible.
5. add_plan: This function is used to save a plan's data into the database for future comparison. It will ensure no duplicate plan names are saved.
6. get_plans: This function is used to get all plans that are saved in the database for users to reference
7. get_table_for_apv: This is the data input validation function when users attempt to calculate the APV, it validates the input then calls calc_insurance_value for the actual calculation

#### apv.html
This renders the HTML page with a few naunce. First, only the input form will be rendered if there are no data for apv's details -> this is the default page. If backend responded with APV detailed table, then it must mean a valid form was filled or there is a valid GET redirect request from the comparison page. If this is the case, it will render the full tables with all associated details and also ask users if they want to save the plan.

#### compare.html
This renders the page for comparison purposes. It simply ask for data from the backend on all saved plans and sort it from most valuable to least and renders it. Each saved plan will also have a button for viewing it's details. This button is a redirect to the apv page with all the GET URL arguments pre-filled with each row's plan parameters.

#### index.html
Nothing much that is special here except that long sections of text is collapsible if the user so wish.

#### tables.html
Ask users to choose a specific life table to view, this can be defined by just 2 form input: sex and year. The form involves a dynamic dropdown where only the years where lifetables are available will be shown.

#### layout.html
The default page layout that all other HTML extends from. It defines the 4 link to individual pages on the header, and a footer containing the disclaimer.

#### Other files
- lifetables.csv for lifetable data import, this file is downloaded form Singapore's Department of Statistics. Can be replaced by other country's data as long as the data is in the right format.
- lifetables.db as an sqlite3 database to store relevant data for future retrival.
- styles.css provide minimal site formatting, the heavy lifitng is done by bootstrap
- Other standard repository files such as an opensource license, requirement.txt for the required libraries, .gitignore for files to ignore, and this README.


