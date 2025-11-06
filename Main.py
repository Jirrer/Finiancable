import PullingData, os
from nicegui import events, ui
from uuid import uuid4

# To-Do: add a way to select the month


UPLOAD_LOSS_FOLDER = os.path.join(os.getcwd(), 'loss_pdfs')
UPLOAD_GAINS_FOLDER = os.path.join(os.getcwd(), 'gain_pdfs')

def root():
    with ui.row().classes('w-full m-0 p-0 gap-0 rowBackground'):
        ui.link('Charts', '/').classes('pageButton')
        ui.link('Log', '/other').classes('pageButton')

    ui.separator()
    ui.sub_pages({'/': chartsPage, '/other': logPage})

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


def chartsPage():
    ui.label("Charts Page")


def logPage():
    with ui.row():
        with ui.column():
            ui.label("Loss Input")
            ui.upload(on_upload=handle_loss_upload).classes('max-w-full')

        with ui.column():
            ui.label("Gains Input")
            ui.upload(on_upload=handle_gains_upload).classes('max-w-full')

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
    ui.run_javascript('location.reload()')

    print("Running Report...")

    if PullingData.runMonthlyReport(): print("Data Added")

    if PullingData.clearPdfFolders(): print("PDFs removed")

    print("Finished Report")


ui.run(root, native=True)