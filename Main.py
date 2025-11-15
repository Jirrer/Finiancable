import PullingData, os
from nicegui import events, ui
from uuid import uuid4
from MiscMethods import labelToDate, monthToWord

# File Paths
UPLOAD_LOSS_FOLDER = os.path.join(os.getcwd(), 'loss_pdfs')
UPLOAD_GAINS_FOLDER = os.path.join(os.getcwd(), 'gain_pdfs')

# Global Vars
state = {'selected_date': None}

def root():
    with ui.row().classes('w-full m-0 p-0 gap-0 rowBackground'):
        ui.link('Charts', '/').classes('pageButton')
        ui.link('Log', '/log').classes('pageButton')
        ui.link('settings', '/settings').classes('pageButton')

    ui.separator()
    ui.sub_pages({'/': chartsPage, '/log': logPage, '/settings': settingsPage})

    ui.add_css('''      
    .rowBackground {
        background-color: lightblue;  
        width: 100%;
        padding: 0;                  
        margin: 0;                    
        display: flex;                
        box-sizing: border-box;
    }
    .pageButton {
        margin: 0 !important;       
        padding: 0 !important;    
        flex: 1;                   
        text-align: center;   
        font-family: Arial, sans-serif;
        font-size: 3rem;
        font-weight: 100;
        text-decoration: none;
        color: black;
        background-color: #808080;
        display: flex;               
        justify-content: center;
        align-items: center;
        height: 10vh;
        box-sizing: border-box;            
    }
               
    .pageButton:hover {
        background-color: #0056b3;
    }
             
''')
    
def settingsPage():
    # contentLabel = ui.label()

    with ui.row():
        with ui.column():
            ui.label("input pdf")
            ui.upload(on_upload=getContent)
        
        with ui.column():
            ui.label("enter regex")

async def getContent(e: events.UploadEventArguments):
    file = e.file

    text = await PullingData.pullRawData(file)

    ui.label(text)


def chartsPage():
    ui.date(value='2025-01-01', on_change=lambda e: getChart(e.value))
    
    yearData = ui.label()

    with ui.row().style('width: 90vw; height: 50vh; margin: 0; padding: 0;'):
        chart = ui.echart({
            'xAxis': {'type': 'category', 'data': []},
            'yAxis': {'axisLabel': {':formatter': 'value => "$" + value'}},
            'series': [{'type': 'line', 'data': []}],
        }).style('width: 100%; height: 100%;')

    def getChart(yearInput: str):
        if yearInput:
            year = yearInput[:4]
            yearData.set_text(f'Profits For {year}')

            dates, values = getChartValue(yearInput)

            chart.options['xAxis']['data'] = dates
            chart.options['series'][0]['data'] = values
            chart.update()

def getChartValue(yearData: str):
    year = yearData[:4]
    userData = PullingData.getUserData()

    dates, values = [], []
    for key, val in userData.items():
        if key[3:] == year:
            dates.append(monthToWord(key[0:2]))
            values.append(val['Profit/Loss'])

    return dates, values

def logPage():
    ui.date(value='2025-01-01', on_change=lambda e: chosenDate.set_text(e.value))
    chosenDate = ui.label()

    with ui.row():
        with ui.column():
            ui.label("Loss Input")
            ui.upload(on_upload=handle_loss_upload).classes('max-w-full')

        with ui.column():
            ui.label("Gains Input")
            ui.upload(on_upload=handle_gains_upload).classes('max-w-full')

    state['selected_date'] = chosenDate

    ui.button("Generate Report", on_click=logData)

async def handle_loss_upload(e: events.UploadEventArguments):
    uploaded_file = e.file

    save_path = os.path.join(UPLOAD_LOSS_FOLDER, uploaded_file.name)

    await uploaded_file.save(save_path) 

    ui.notify(f'File saved at: {save_path}')

async def handle_gains_upload(e: events.UploadEventArguments):
    uploaded_file = e.file

    save_path = os.path.join(UPLOAD_GAINS_FOLDER, uploaded_file.name)

    await uploaded_file.save(save_path) 

    ui.notify(f'File saved at: {save_path}')

def logData():
    if not state['selected_date'].text:
        print("Error - select date")
        return 
    
    ui.run_javascript('location.reload()')

    print("Running Report...")

    if PullingData.runMonthlyReport(labelToDate(state['selected_date'].text)): print("Data Added")

    if PullingData.clearPdfFolders(): print("PDFs removed")
    
    print("Finished Report")

ui.run(root, native=True)