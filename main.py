import kivy

kivy.require('1.0.6')

from kivy.app import App
from kivy.config import Config

Config.set('graphics', 'width', 720)
Config.set('graphics', 'height', 1520)
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ListProperty, DictProperty
from kivymd.toast import toast
from MatrizIden import IdentidadPlan
import sympy as sp
from decimal import  Decimal
import numpy as np
from kivy.uix.screenmanager import FadeTransition

Builder.load_file('./filekv/simplex.kv')


class ParamDatos(Screen):
    pass


class ModeloEntrada(Screen):
    pass

class VistaIteraciones(Screen):
    pass


class VistaManager(ScreenManager):
    NumVar = NumericProperty(0)
    NumRes = NumericProperty(0)
    ModelInter = DictProperty({})
    ModelData = DictProperty({})
    MatrizIteraciones=ListProperty([])
    solucion=ListProperty([])

    M = sp.Symbol('M')

    def __init__(self, **kwargs):
        super(VistaManager, self).__init__(**kwargs)
        self.transition=FadeTransition()
        self.ModeloIterUno=None
        self.ModeloIterDos=None
        self.EncaLate=None
        self.EncaTop=None
        self.tipo = self.ids['modelIn'].ids['spitipo'].text
        print(self.ids['modelIn'].ids)
        self.ids['param'].ids['btnParam'].bind(on_press=self.pasar_param)  # Enlazando el evento al boton ya que los
        # Elemento se generaran de forma dinamica
        self.ids['modelIn'].ids['btn_res'].bind(on_press=self.resolver_model)
        self.ids['modelIn'].ids['btn_return'].bind(on_press=self.regresar_in)
        self.ids['ViewIter'].ids['btn_return_model'].bind(on_press=self.regresar_model)

    def regresar_in(self, pos):
        self.ids['modelIn'].manager.current = 'parametros'

    def regresar_model(self, pos):
        self.ids['ViewIter'].manager.current='modelo'

    def resolver_model(self, pos):
        vectz = self.ModelInter['txtvectz']
        dateZ = []
        estado=True

        for caja in vectz:
            if len(caja.text)==0:
                estado=False
            else:
                dateZ.append(caja.text)  # Obteniendo los valores de la funcion z

        self.ModelData['dateZ'] = dateZ

        modeloDatos = self.ModelInter['txtRestric']
        modelDate = []
        for fila in modeloDatos:
            fila_dato = []
            for caja in fila:
                if len(caja.text)==0:
                    estado=False
                    break
                else:
                    fila_dato.append(caja.text)
            modelDate.append(fila_dato)

        self.ModelData['dateRestric'] = modelDate  # agregando los datos de las restricciones al model data

        txtdesi = self.ModelInter['txtdesi']
        desi = []
        for des in txtdesi:
            if len(des.text)==0:
                estado=False
            else:
                desi.append(des.text)
        self.ModelData['desi'] = desi

        txtbi = self.ModelInter['txtBi']
        dataBi = []
        veribi=True#servira para saber si todos los bi son positivos si alguno es negativo enviara un mensaje
        for bi in txtbi:
            if len(bi.text)==0:
                estado=False
            else:
                if Decimal(bi.text)<0:
                    veribi=False
                else:
                    dataBi.append(bi.text)

        if veribi==False:
            toast('Los Bi no pueden ser negativos considere replantear la ecuacion..', duration=10)
        else:
            if estado==True:#si al recorrer todas las cajas de texto ninguna estaba vacia entonces se proseguira a resolver el problema
                self.ModelData['dateBi'] = dataBi  # agregando los Bi al modelData
                self.ModelData['tipo'] = self.ids['modelIn'].ids['spitipo'].text

                Op = IdentidadPlan(modelData=self.ModelData)
                # Aqui se obtienen dos elementos la MatrixIdent del la matriz generada y el enca que son sus respectivos Esncabezados
                MatrixComponen = Op.MatrizIdentidadBi()

                # Aqui se obtiene la matriz de restricciones unida a el Vector Z
                MatrRestrZ = Op.RestricMasZ()

                # Obteniendo la Matriz identidad
                MatrizIden = MatrixComponen.get('matrixIdent')
                # Obteniendo el encabezado de arriba
                encaPart = MatrixComponen.get('enca')

                self.EncaTop = Op.EncabezadoTop(encaPart, self.NumVar)  # Encabezado de arriba el cual se complementa con x1, x2,...xn
                self.EncaLate = MatrixComponen.get('encaLate')  # Encabezado Lateral


                self.ModeloIterUno=Op.ModeloIterUno(MatrRestrZ, MatrizIden)#Tabla inicial
                self. ModeloIterDos=Op.ModeloIterDos(self.EncaLate, self.ModeloIterUno)

                if self.ModeloIterDos is None:#Se verifica hubo una segunda iteracion que es la de sumar las m y ontener una solucion inicial
                    self.ModeloIterDos=self.ModeloIterUno#ya que si no hay para seguir trabajando solo con una matriz se igualara la matriz iter dos con la uno para
                #print(self.ModeloIterUno)
                #print(self.ModeloIterDos)

                #print('Este es el tipo: '+self.ids['modelIn'].ids['spitipo'].text)
                resultados = Op.Iteraciones(self.ModeloIterDos, self.ModeloIterUno, self.ids['modelIn'].ids['spitipo'].text, self.EncaTop, self.EncaLate)
                self.MatrizIteraciones=resultados.get('MatrizIteraciones')
                self.solucion=resultados.get('Soluciones')

                #print(self.MatrizIteraciones)

                self.ids['ViewIter'].manager.current='view' #Pasando a la siguiente pantalla

                self.ids['ViewIter'].ids['tabla_desig'].cols=len(self.EncaTop)
                self.ids['ViewIter'].ids['tabla_data'].data=self.MatrizIteraciones
                self.ids['ViewIter'].ids['solucion'].data=self.solucion
            else:
                toast("Debe llenar todos los campos para poder resolver el problema...")









    def pasar_param(self, pos):
        if len(self.ids['param'].ids['NumVar'].text)>0 and len(self.ids['param'].ids['NumRes'].text)>0:
            self.NumVar = int(self.ids['param'].ids['NumVar'].text)
            self.NumRes = int(self.ids['param'].ids['NumRes'].text)
            if self.NumVar>=2 and self.NumVar<=10 and self.NumRes>=2 and self.NumRes<=10:
                print('Numero de Variables: ' + str(self.NumVar) + '\nNumero de Restricciones: ' + str(self.NumRes))
                # modelI es el id de la clase que se abre
                # func_z es el id del BoxLayout que contendra los campos de la funcion Z
                # Creando la funcion Z
                vectz = []
                for i in range(self.NumVar):
                    vectz.append(TextInput(multiline=False, input_filter='float'))
                sub = 0
                for i in vectz:
                    sub = sub + 1
                    substr = ''
                    if i is not vectz[len(vectz) - 1]:
                        substr = str(sub) + '+'
                    else:
                        substr = str(sub)

                    self.ids['modelIn'].ids['func_z'].add_widget(i)
                    self.ids['modelIn'].ids['func_z'].add_widget(Label(text='X' + substr))

                self.ModelInter['txtvectz'] = vectz  # Agregando el diccionario al diccionario

                modelData = []
                # Creando la funcion de restricciones
                self.ids['modelIn'].ids['restric'].cols = self.NumVar + self.NumVar
                for i in range(self.NumRes):
                    listaRestric = []
                    for j in range(self.NumVar):
                        listaRestric.append(TextInput(multiline=False, input_filter='float'))
                    modelData.append(listaRestric)

                sub = 0
                for fila in modelData:
                    for inputText in fila:
                        sub = sub + 1
                        substr = ''
                        if inputText is not fila[len(fila) - 1]:
                            substr = str(sub) + '+'
                        else:
                            substr = str(sub)

                        self.ids['modelIn'].ids['restric'].add_widget(inputText)
                        self.ids['modelIn'].ids['restric'].add_widget(Label(text='X' + substr))
                    sub = 0
                self.ModelInter['txtRestric'] = modelData  # Agregando los datos de las restricciones al diccionario

                desigual = ('<=', '>=', '=')
                vect_desi = []
                for i in range(self.NumRes):
                    vect_desi.append(Spinner(text='<=', values=desigual))

                for i in vect_desi:
                    self.ids['modelIn'].ids['desi'].add_widget(i)

                self.ModelInter['txtdesi'] = vect_desi  # Agregando el Vector de desigualdades

                vectBi = []
                for i in range(self.NumRes):
                    vectBi.append(TextInput(multiline=False, input_filter='float'))

                for i in vectBi:
                    self.ids['modelIn'].ids['bi'].add_widget(i)

                self.ModelInter['txtBi'] = vectBi  # Agregando el Vector de cajas de texto BI

                # print(self.ModelInter)

                # print(self.ModelIn)

                self.ids['modelIn'].manager.current = 'modelo'
            else:
                toast('El Numero de variables tiene que ser>=2 y  <=10 y el numero de restricciones debe de ser >=2 y <=10', duration=15.0)
        else:
            toast('Debe de ingresar el numero de variables y el numero de restricciones para poder continuar..', 10)


class MainApp(App):
    title = 'Metodo Simplex'

    def build(self):
        return VistaManager()


if __name__ == '__main__':
    MainApp().run()
