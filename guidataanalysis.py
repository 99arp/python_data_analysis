
import sys
import pandas as pd
import numpy as np
import webbrowser
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QErrorMessage, QMenu, QAction
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import singlecurve as sc
import multiplecurve as mc
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.single_curve_data = pd.DataFrame()
        self.big_curve_data = pd.DataFrame()
        self.splitted_big_data = pd.DataFrame()
        self.curve_parameters = pd.DataFrame()
        self.curve_parameters_scatter = pd.DataFrame()
        self.result_of_analysis = pd.DataFrame()
        self.data_to_be_checked = pd.DataFrame()
        self.experiment_start_index_big_data = [] #_corresponding_end_element_in_end_array
        self.experiment_end_index_big_data= []  #corresponding_start_element_in_start_array 
        self.concentration_for_sensitivity = []

        uic.loadUi("gui.ui", self)
        self.GraphArea = PlotCanvas(self, width = 9, height = 7)
        self.GraphArea.move(120,60)

      
       # self.GraphArea.setFocus()
        self.setWindowTitle("Curve Analysis Tool")
        self.documentation_menu = QtWidgets.QMenu('&Documentation', self)
        newAct = QAction('Open', self)
        self.documentation_menu.addAction(newAct)
        self.documentation_menu.triggered.connect(self.open_documentation)
        self.menuBar().addMenu(self.documentation_menu)
            
     

        self.LoadData.clicked.connect(self.get_singlecurve_files)
        self.ExperimentNumber.valueChanged.connect(self.on_value_changed_A)
        self.Smoothing.valueChanged.connect(self.on_value_changed_A)
        self.ReadyArea.setStyleSheet("background-color: yellow")
        self.ReadyArea.setText("No Data")
        self.CompareCB.stateChanged.connect(self.on_value_changed_A)
       # self.DrawDerivativeCBA.stateChanged.connect(self.draw_derrivative)
        
        
        
        self.LoadDataB.clicked.connect(self.get_big_data_files)
        self.ExperimentNumberB.valueChanged.connect(self.on_value_changed_experiment_number_B)
        self.PlotDataNrSpinnerB.valueChanged.connect(self.on_value_changed_plot_data_number)
        self.UseTimeStampCB.toggled.connect(lambda: self.UseDerivativeCB.setChecked(False))
        self.UseDerivativeCB.setEnabled(False)
        self.UseTimeStampCB.stateChanged.connect(self.on_method_change)
        self.UseDerivativeCB.stateChanged.connect(self.on_method_change)
        
        
        self.ExportExcelB.clicked.connect(self.export_results)
        self.ReadyAreaB.setStyleSheet("background-color: yellow")
        self.ReadyAreaB.setText("No Data")   
        self.BaselineBCB.stateChanged.connect(lambda: self.GraphArea.scatter(self.curve_parameters_scatter['Temperature'], self.curve_parameters_scatter ['Baseline'], 'Current (nA)'))
        self.IStableBCB.stateChanged.connect(lambda: self.GraphArea.scatter(self.curve_parameters_scatter['Temperature'], self.curve_parameters_scatter ['I Stable'], 'Current (nA)'))
        self.I90BCB.stateChanged.connect(lambda: self.GraphArea.scatter(self.curve_parameters_scatter['Temperature'], self.curve_parameters_scatter ['I 90'], 'Current (nA)'))
        self.T90BCB.stateChanged.connect(lambda: self.GraphArea.scatter(self.curve_parameters_scatter['Temperature'], self.curve_parameters_scatter ['T 90'], 'time (s)'))
        self.F90BCB.stateChanged.connect(lambda: self.GraphArea.scatter(self.curve_parameters_scatter['Temperature'], self.curve_parameters_scatter ['F 90'], 'time (s)'))
        self.SensitivityBCB.stateChanged.connect(lambda: self.GraphArea.scatter(self.curve_parameters_scatter['Temperature'], self.curve_parameters_scatter ['Sensitivity'], 'nA / ppm'))
 
     
    def get_singlecurve_files(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file", "/Users/03abc/Desktop/python", "*.xlsm *.xls *.xlsx")
        
        if fileName:
            self.single_curve_data = pd.read_excel(fileName)
            self.ReadyArea.setStyleSheet("background-color: #00ff40")
            self.ReadyArea.setText("Ready")
            self.ExperimentNumber.setMaximum(len(self.single_curve_data.columns) )
            
    def get_big_data_files(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file", "/Users/03abc/Desktop/python", "*.xlsm *.xls *.xlsx")
        
        if fileName:
            self.big_curve_data = pd.read_excel(fileName)
            self.concentration_for_sensitivity = np.asarray(self.big_curve_data.iloc[0])
            self.concentration_for_sensitivity = self.concentration_for_sensitivity[7:] # 7 becasue experiment starts at 7
            self.big_curve_data = self.big_curve_data.iloc[1:]
            self.ReadyAreaB.setStyleSheet("background-color:#00ff40")
            self.ReadyAreaB.setText("Ready")
            self.splitted_big_data = mc.split_big_data(self.big_curve_data)
            self.experiment_start_index_big_data , self.experiment_end_index_big_data= mc.get_start_end_index(self.big_curve_data)
            self.curve_parameters = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = self.UseTimeStampCB.isChecked(), for_plotting = True)
            self.curve_parameters_scatter = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = self.UseTimeStampCB.isChecked(), for_plotting = False)
            self.curve_parameters_scatter['Sensitivity'] = self.curve_parameters['I Stable'] / self.concentration_for_sensitivity[self.ExperimentNumberB.value()-1]
            self.ExperimentNumberB.setMaximum(len(self.big_curve_data.columns) -7) #because data starts at 7th column
            self.PlotDataNrSpinnerB.setMaximum(len(self.splitted_big_data.columns) -0) #becasue index starts at 0 
            
            self.ExperimentNumberB.setValue(1) #right after loading set value to 1
            self.PlotDataNrSpinnerB.setValue(1) #first curve of first experiment
    
    
    def open_documentation(self):
        webbrowser.open('http://wiki.msasafety.com/display/STUDI/Curve+Analysis+Tool')
        
    def export_results(self):
        if(self.UseTimeStampCB.isChecked()):
            self.curve_parameters = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = True, for_plotting = False)
         
        else:
            self.curve_parameters = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = False, for_plotting = False)
        self.curve_parameters['Sensitivity'] = self.curve_parameters['I Stable'] / self.concentration_for_sensitivity[self.ExperimentNumberB.value()-1]
        self.curve_parameters.to_excel("Curve_Parameters_Experiment_"+str(self.ExperimentNumberB.value()) +"Timestamp_"+str(self.UseTimeStampCB.isChecked())+ "_Smoothing_"+str(self.SmoothingSpinnerB.value())+".xlsx")
    
    def get_experiment_number_data(self,data, data_number = 0):
        return data.iloc[:,data_number]    
    def on_value_changed_plot_data_number(self):
        splitted_data = self.splitted_big_data
        data_ = self.get_experiment_number_data(splitted_data, self.PlotDataNrSpinnerB.value()-1) #-1 because of indexing
        data_with_smoothing_ = sc.movingmean_calculator(data_, self.SmoothingSpinnerB.value())
        self.plot_single_data_multiple_curve(data_with_smoothing_)
        
        
        

      

    def on_method_change(self):
        if(self.UseTimeStampCB.isChecked()):
            self.curve_parameters = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = True, for_plotting = True)
            self.curve_parameters_scatter = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = True, for_plotting = False)
        else:
            self.curve_parameters = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = False, for_plotting = True)
            self.curve_parameters_scatter = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = False, for_plotting = False)
        self.curve_parameters['Sensitivity'] = self.curve_parameters['I Stable'] / self.concentration_for_sensitivity[self.ExperimentNumberB.value()-1]
        self.curve_parameters_scatter['Sensitivity'] = self.curve_parameters['I Stable'] / self.concentration_for_sensitivity[self.ExperimentNumberB.value()-1]
        splitted_data = self.splitted_big_data
        data_ = self.get_experiment_number_data(splitted_data, self.PlotDataNrSpinnerB.value())
        data_with_smoothing_ = sc.movingmean_calculator(data_, self.SmoothingSpinnerB.value())
        self.plot_single_data_multiple_curve(data_with_smoothing_)
        
        return
   
    
    def on_value_changed_experiment_number_B(self):
       self.splitted_big_data = mc.split_big_data(self.big_curve_data, dataset_number= self.ExperimentNumberB.value()-1)
       if(self.UseTimeStampCB.isChecked()):
            self.curve_parameters = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = True, for_plotting = True)
            self.curve_parameters_scatter = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = True, for_plotting = False)
       else:
            self.curve_parameters = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = False, for_plotting = True)
            self.curve_parameters_scatter = mc.get_curve_parameters_from_big_data(self.splitted_big_data, timestamp = False, for_plotting = False)
       self.curve_parameters['Sensitivity'] = self.curve_parameters['I Stable'] / self.concentration_for_sensitivity[self.ExperimentNumberB.value()-1]
       self.curve_parameters_scatter['Sensitivity'] = self.curve_parameters['I Stable'] / self.concentration_for_sensitivity[self.ExperimentNumberB.value()-1]
       splitted_data = self.splitted_big_data
       data_ = self.get_experiment_number_data(splitted_data, self.PlotDataNrSpinnerB.value()-1) #index matching
       data_with_smoothing_ = sc.movingmean_calculator(data_, self.SmoothingSpinnerB.value())
       self.plot_single_data_multiple_curve(data_with_smoothing_)
       if(self.AutoExportBCB.isChecked()):
           self.export_results()
       


             
        
             
        
    def on_value_changed_A(self):
        data_without_smoothing, data_with_smoothing, data_with_smoothing_mean = self.prepare_data(self.single_curve_data, self.ExperimentNumber.value(),
                                                  self.Smoothing.value())
        baseline_value = sc.baseline_calculator(data_with_smoothing); 
        self.show_data_quality(data_without_smoothing)
        self.GraphArea.figure.clear()
        quality_of_data = sc.check_quality_of_data(data_with_smoothing)
        if(quality_of_data[2] == 'bad'):  #because this information is saved on third array element, there is definetely more pythonic way to do it
            error_dialog = QErrorMessage()
            error_dialog.showMessage("Bad Data Quality, Consider Increasing Smoothing")
            error_dialog.exec_()
        else: 
        
            if self.DrawLinesOnGraphCB.isChecked():
               # self.GraphArea.draw_lines(baseline_value)
                self.draw_lines_on_graph(data_with_smoothing, single_curve = True)
                
            if self.CompareCB.isChecked():
               self.GraphArea.plot(data_without_smoothing)
               self.GraphArea.plot(data_with_smoothing)
               self.GraphArea.plot(data_with_smoothing_mean)
         #      self.GraphArea.plot()
            if self.DrawDerivativeCBA.isChecked():
                self.GraphArea.plot(sc.derrivative_calculator(data_with_smoothing))
                  
                
              
                
            if self.Smoothing.value() != 0:
                self.GraphArea.plot(data_with_smoothing)
            else:
                self.GraphArea.plot(data_without_smoothing)
                
    def prepare_data(self, data, index = 1, smoothing = 0):
        data_without_smoothing_ = data.iloc[:,index]
        data_without_smoothing_ = data_without_smoothing_.dropna()
        data_with_smoothing_ = pd.Series([])
        data_with_smoothing_mean_ = pd.Series([])
        if smoothing != 0:
            data_without_smoothing_ = data.iloc[:,index]
            data_with_smoothing_ =  sc.movingmedian_calculator(data_without_smoothing_, smoothing)
            data_with_smoothing_mean_= sc.movingmean_calculator(data_without_smoothing_, smoothing)
        return data_without_smoothing_, data_with_smoothing_, data_with_smoothing_mean_
            
             
    
    def show_data_quality(self, data):
           std_max_diff, std_min_diff,data_quality  =  sc.check_quality_of_data(data)
           if(data_quality == 'good' ):
               self.DataQualityButton.setStyleSheet("background-color:#00ff40")
               self.DataQualityButton.setText("Good \n Data Quality")
               
           elif(data_quality == 'medium' ):
               self.DataQualityButton.setStyleSheet("background-color:yellow")
               self.DataQualityButton.setText("Medium \n Data Quality")
           elif(data_quality =='bad' ):
               self.DataQualityButton.setStyleSheet("background-color:red")
               self.DataQualityButton.setText("Bad \n Data Quality")
              # error_dialog = QErrorMessage()
              # error_dialog.showMessage("Bad Data Quality, Consider Increasing Smoothing")
               #error_dialog.exec_()
               #Additional Feature, implementation of pop up     
                      
           
    def draw_lines_on_graph(self, Data,  single_curve, begasung_start = 0, begasung_end = 0 ):
        if(single_curve == True):
            curve_parameters = sc.parameter_calculator(Data, timestamp = False, for_plotting = True)
        else: 
            curve_parameters = sc.parameter_calculator(Data, timestamp = self.UseTimeStampCB.isChecked(), for_plotting = True)
        
        i_stable = curve_parameters[0]
        i_90 = curve_parameters[1]
        i_10 = curve_parameters[2]
        t_90 = curve_parameters[3]
        f_90 = curve_parameters[4]
        baseline = curve_parameters[5]
  
        
        curve_rising = sc.determine_curve_rising_or_falling(Data)
        if(begasung_start == 0 and begasung_end == 0):
            if (curve_rising == True):
                probable_gas_end, probable_gas_start = sc.determine_position_of_min_max_derrivative(Data)
           
            else:
                probable_gas_start, probable_gas_end = sc.determine_position_of_min_max_derrivative(Data)
        else:
            probable_gas_start, probable_gas_end = begasung_start, begasung_end
        
        self.GraphArea.figure.add_subplot(111).axhline(i_stable, color = 'm', ls = '-.', label ="I Stable: " +str(round(i_stable,2)) + " nA")
        self.GraphArea.figure.add_subplot(111).axhline(baseline, color = 'k', ls = 'solid', label ="Baseline: "+ str(round(baseline,2)) +" nA")
        self.GraphArea.figure.add_subplot(111).axhline(i_90, color = 'm', ls = '-.', label ="I 90: "+ str(round(i_90 ,2)) + " nA")
        self.GraphArea.figure.add_subplot(111).axvline(probable_gas_start, color = 'r', ls = 'solid')
        self.GraphArea.figure.add_subplot(111).axvline(probable_gas_end, color = 'r', ls = 'solid')
        self.GraphArea.figure.add_subplot(111).axvline(t_90,color = 'r', ls = ':', label ="T 90: "+ str(abs(round(t_90-probable_gas_start,2))) + " s")
        self.GraphArea.figure.add_subplot(111).axvline(f_90, color = 'r', ls = ':', label ="F 90: "+ str(abs(round(f_90-probable_gas_end,2))) + " s")

        self.GraphArea.figure.add_subplot(111).legend()
        if(single_curve == False):
            temperature_values = np.asarray(self.curve_parameters['Temperature'])   
            self.GraphArea.figure.add_subplot(111).set_title( "Data Nr." +str(self.PlotDataNrSpinnerB.value()) + "@ Temp = " +str(temperature_values[self.PlotDataNrSpinnerB.value() -1]) + " ° C and Concentration "+ str(self.concentration_for_sensitivity[self.ExperimentNumberB.value() -1]) +" ppm" )
            
   
    def plot_single_data_multiple_curve(self, data):
        self.GraphArea.figure.clear() 
        if(self.UseTimeStampCB.isChecked()):
            start, end = self.experiment_start_index_big_data[self.PlotDataNrSpinnerB.value()-1], self.experiment_end_index_big_data[self.PlotDataNrSpinnerB.value()-1] #because of zero based indexing
            self.draw_lines_on_graph(data, False, mc.data_start, len(data)-mc.data_end ) #second argument is singlue_curve_false
            self.GraphArea.plot(data)
        else:
            self.draw_lines_on_graph(data, single_curve = False)
            self.GraphArea.plot(data)
      
            
        

            
        
    # def remove_nan_values(self, data):
    #     numpy_array_of_data = np.array(data)
    #     filter = ~np.isnan(numpy_array_of_data)
    #     return numpy_array_of_data[filter]
    
  
        
 

        
        
class PlotCanvas(FigureCanvas):
   
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

       
        


    def plot(self, data):
                     
        
        #self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot( data)
        ax.margins(0, 0.05)
        ax.set_xlabel('Time (s) ')
        ax.set_ylabel('Current (nA) ')
        #ax.set_title('PyQt Matplotlib Example')
        self.draw()

    def scatter(self, temperature_data, data_to_be_scattered, datatype = ""):
        self.figure.clear()
        ascatter = self.figure.add_subplot(111)
        ascatter.scatter(temperature_data, data_to_be_scattered)
        ascatter.set_xlabel('Temperature in ° C')
        ascatter.set_ylabel(datatype) 
        self.draw()
        
    
      
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
