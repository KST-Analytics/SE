# Load useful Python modules
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import matplotlib.dates as mdates


def load():
    SE_PV = pd.read_pickle('/content/drive/MyDrive/Invoice2_Deliverables/d_Eastover_iPV_185_240ft_Jul6_Dec28')
    SE_tags = pd.read_pickle('/content/drive/MyDrive/Invoice2_Deliverables/d_Eastover_iTAG_185_240ft_Jul6_Dec28')
    SE_tags.loc['Short'][27:] = SE_PV.columns[27:].values
    SE_hmap = pd.read_pickle('/content/drive/MyDrive/Invoice2_Deliverables/d_Eastover_iHMAP_185_240ft_Jul6_Dec28')

    return SE_PV, SE_tags, SE_hmap


def iVis():
    mill_tags = {'Mill SE': SE_tags}
    mill_data = {'Mill SE': SE_PV}
    mill_hmap = {'Mill SE': SE_hmap} 

    PV_W = widgets.Dropdown(options = mill_tags['Mill SE'].columns.tolist(), description = 'PV')

    y_slider_W = widgets.IntSlider(max = 2021, value=2021, step=1, description='year')
    m_slider_W = widgets.IntSlider(min=7,max=12, value=8, step=1, description='month')
    w_slider_W = widgets.IntSlider(min=12,value=120, step=12, description='window size')
    d_slider_W = widgets.IntSlider(min=1,max=31,value = 10,  step=1, description='day')
    h_slider_W = widgets.IntSlider(min=0,max=24, value = 12, step=1, description='hour')
    
    def hmap_interact(PV, y_slider,m_slider,d_slider, h_slider, w_slider):
        DF = mill_hmap['Mill SE']
        df = mill_data['Mill SE']
        tags = mill_tags['Mill SE']

        y_slider_W.min = DF.columns[0].year
        w_slider_W.max = len(DF.T)

    # This code accounts for the manual selector for year/month/day/hour
        dt = pd.DataFrame({'year': y_slider,
                    'month': m_slider,
                    'day': d_slider,
                    'hour': h_slider}, index=[0])
        dt = pd.to_datetime(dt)
        # We find the row # of df that matches the value of dt (from the user)
        j = DF.T.index.get_loc(dt.iloc[0])

        SMALL_SIZE = 18     #Font sizes
        MEDIUM_SIZE = 20
        BIGGER_SIZE = 20
        #plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
        plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
        plt.rc('axes', labelsize= MEDIUM_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
        
        fig, ax = plt.subplots(2,figsize=(30,15))
        plt.style.use("ggplot")
        #im = ax[0].imshow(DF.iloc[:,j:j+w_slider],aspect = 'auto', cmap='magma', vmin= 0, vmax = 350 + 10)
        im = ax[0].imshow(DF.iloc[:,j:j+w_slider],aspect = 'auto', cmap='magma')
        cbar = ax[0].figure.colorbar(im, ax=ax)#[0])     # Create colorbar
        cbar.set_label(label="Temperature ($^\circ$F)", rotation=-90, va="bottom", fontsize=18)

        # THIS CODE IS FOR THE HEATMAP
        ax[0].tick_params(axis='both', direction='out')
        ax[0].set_xticks([0,int((w_slider)/4),int((w_slider)/2),int((w_slider)*3/4),w_slider-1])
        ax[0].set_xticklabels([DF.columns[j],DF.columns[j+int((w_slider)/4)],DF.columns[j+int((w_slider)/2)],
            DF.columns[j+int((w_slider)*3/4)],DF.columns[j+w_slider-1]])    
        ax[0].set_xlabel("Date")
        ax[0].set_ylabel("Distance from firing end of kiln (ft)")
        #ax[0].set_yticks([DF.index[0], DF.index[0+int(np.round(len(DF)/4,0))], 
        #    DF.index[0+2*int(np.round(len(DF)/4,0))], DF.index[0+3*int(np.round(len(DF)/4,0))], DF.index[-1]])
        ax[0].set_yticks([0, int(np.round(len(DF)/4,0)), 2*int(np.round(len(DF)/4,0)), 
            3*int(np.round(len(DF)/4,0)), len(DF)]) 
        ax[0].set_yticklabels([np.round(DF.index[0],1), np.round(DF.index[0+int(np.round(len(DF)/4,0))],1), 
            np.round(DF.index[0+2*int(np.round(len(DF)/4,0))],1), np.round(DF.index[0+3*int(np.round(len(DF)/4,0))],1), np.round(DF.index[-1],1)])
        
        ln1, = ax[1].plot(pd.Series(data=df[tags[PV].loc['Short']].values[j:j+w_slider]),
            label = str(PV) + '\n' + tags[PV].loc['Tag'])

        ax[1].autoscale(enable=True, axis='x', tight=True)
        ax[1].legend(handles=[ln1],loc="upper right")
        ax[1].set_xlabel("Date")
        ax[1].set_ylabel(str(PV) + ' (' + tags[PV].loc['Unit'] + ')')
        
        ax[1].set_xticks([0,int((w_slider)/4),int((w_slider)/2),int((w_slider)*3/4),w_slider-1])
        ax[1].set_xticklabels([DF.columns[j],DF.columns[j+int((w_slider)/4)],DF.columns[j+int((w_slider)/2)],
            DF.columns[j+int((w_slider)*3/4)],DF.columns[j+w_slider-1]])

        plt.show()

    ui0 = widgets.VBox([y_slider_W,m_slider_W])
    ui1 = widgets.VBox([d_slider_W,h_slider_W])
    ui2 = widgets.VBox([w_slider_W,PV_W])
    ui4 = widgets.HBox([ui0,ui1,ui2])
    out = widgets.interactive_output(hmap_interact, {'PV': PV_W, 'y_slider': y_slider_W,
                                        'm_slider':m_slider_W, 'w_slider': w_slider_W, 'd_slider': d_slider_W,
                                        'h_slider': h_slider_W})

    display(ui4, out)
