import PullingData
from nicegui import ui
from uuid import uuid4


def root():
    with ui.row().classes('w-full m-0 p-0 gap-0 rowBackground'):
        ui.link('Charts', '/').classes('pageButton')
        ui.link('Log', '/other').classes('pageButton')

    ui.separator()
    ui.sub_pages({'/': chartsPage, '/other': logPage})

    ui.add_css('''      
    .rowBackground {
        background-color: lightblue;  /* change to any color or use an image */
        width: 100%;
        padding: 0;                   /* optional */
        margin: 0;                    /* optional */
        display: flex;                /* ensures children align properly */
        box-sizing: border-box;
    }
    .pageButton {
        margin: 0 !important;       
        padding: 0 !important;    
        flex: 1;                   
        text-align: center;   
        font-family: Arial, sans-serif;
        font-size: 1.2rem;
        font-weight: 500;
        text-decoration: none;
        color: black;
        background-color: red;
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
    ui.label("test")


def logPage():
    ui.label("log page")


    



ui.run(root, native=True)
