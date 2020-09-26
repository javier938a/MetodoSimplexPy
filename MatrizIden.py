import numpy as np
from sympy import Rational
from sympy import Symbol
from sympy import sympify
from sympy import N


class IdentidadPlan:
    M = Symbol('M')

    def __init__(self, modelData=None):
        self.modelData = modelData

    def RestricMasZ(self):  # recibe un diccionario con cada Uno de los componentes del problema y genera la matriz
        '''{'dateZ': ['2', '1', '2'], '
            dateRestric': [['1', '1', '2'],
                           ['3', '2', '3'],
                           ['2', '6', '4']],
            'desi': ['<=', '<=', '<='],
            'dateBi': ['3', '4', '3']}'''
        z = self.modelData.get('dateZ')  # Obteniendo el vector z
        vectzStr = np.array(z)  # se pasa a numpy para solo multiplicar *-1
        vectzFloat = vectzStr.astype(np.float)
        vectzNeg = vectzFloat * -1  # multiplicando por  -1 toda la fila z
        # print(vectzNeg.astype(np.str))
        restric = self.modelData.get('dateRestric')
        MatrizRestric = np.array(restric)
        MatrizRestricMasZ = np.append(MatrizRestric, [vectzNeg], axis=0)  # agregando al final la fila z negativa
        # print(MatrizRestric)
        MatrizRestBiListSym = []  # Almacenara los valores de las restricciones en formato sympy
        for fila in MatrizRestricMasZ:
            line = []
            for elem in fila:
                line.append(sympify(elem))
            MatrizRestBiListSym.append(line)
        MatrizRestBiSymNp = np.array(MatrizRestBiListSym)
        return MatrizRestBiSymNp

    def MatrizIdentidadBi(self):
        desi = self.modelData.get('desi')
        tipo = self.modelData.get('tipo')
        print(tipo)
        MatIde = []  # Matriz que servira para almacenar los 1 pero le faltarar ceros a la derecha
        MatrixIden = []  # Matriz identidad completa agregandole lo que falta de ceros
        Enca = []  # Encabezado que tendra estas columnas
        EncaLate = []
        vect_ident_z = []  # Vector que almacenara lo que le correspondra a la fila z en la matriz inicial
        A = 0
        E = 0
        for i in desi:
            if i == '<=':
                sizeMat = len(MatIde)
                if sizeMat == 0:
                    # contador de variables de exceso
                    E += 1
                    Enca.append(('E' + str(E)))
                    EncaLate.append(('E' + str(E)))  # Añadiendolo al Encabezado Lateral
                    vect_1 = ['1']
                    MatIde.append(vect_1)
                    vect_ident_z.append('0')  # Agregando un cero
                else:
                    E += 1  # Contando exesos
                    Enca.append(('E' + str(E)))
                    EncaLate.append(('E' + str(E)))
                    UltVetc = len(MatIde[len(MatIde) - 1])  # calculando el tamaño del ultimo vector agregando
                    ceros = '0' * UltVetc
                    cero_uno = list((ceros + '1'))
                    MatIde.append(cero_uno)
                    vect_ident_z.append('0')  # Agregando un cero
            elif i == '>=':
                sizeMat = len(MatIde)
                if sizeMat == 0:
                    E += 1  # Contando exesos
                    A += 1  # Contando Variables Artificiales
                    Enca.append(('E' + str(E)))
                    Enca.append(('A' + str(A)))
                    vect_1 = ['-1', '1', ]
                    MatIde.append(vect_1)
                    vect_ident_z.append('0')
                    if tipo == 'Maximizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(
                            self.M)  # Agregando un -M porque en la funcion z se penaliza con +M y al pasar al otro lado pasa e restar
                    elif tipo == 'Minimizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(
                            self.M*-1)  # Agregando un M porque en el caso de minimizar se penaliza con -M y al otro lado pasa a sumar
                else:
                    E += 1  # Contando exesos
                    A += 1  # Contando Variables Artificiales
                    Enca.append(('E' + str(E)))
                    Enca.append(('A' + str(A)))
                    UltVetc = len(MatIde[len(MatIde) - 1])  # calculando el tamaño del ultimo vector agregando
                    ceros = '0' * UltVetc
                    ceros_list = list(ceros)
                    ceros_list.append('-1')
                    ceros_list.append('1')
                    MatIde.append(ceros_list)
                    vect_ident_z.append('0')  # Agregando el cero a la variable artificial
                    if tipo == 'Maximizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(self.M )
                    elif tipo == 'Minimizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(self.M*-1)
            elif i == '=':
                sizeMat = len(MatIde)
                if sizeMat == 0:
                    A += 1  # Contando Variables Artificiales
                    Enca.append(('A' + str(A)))
                    vect_1 = ['1', ]
                    MatIde.append(vect_1)
                    if tipo == 'Maximizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(
                            self.M )  # Solo se agrega la M debido a que solo se agrega la variable artificiar en este caso
                    elif tipo == 'Minimizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(self.M*-1)
                else:
                    A += 1  # Contando Variables Artificiales
                    Enca.append(('A' + str(A)))
                    UltVetc = len(MatIde[len(MatIde) - 1])
                    ceros = '0' * UltVetc
                    ceros_list = list(ceros)
                    ceros_list.append('1')
                    MatIde.append(ceros_list)
                    if tipo == 'Maximizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(
                            self.M)  # Solo se agrega la M debido a que solo se agrega la variable artificiar en este caso
                    elif tipo == 'Minimizar':
                        EncaLate.append(('A' + str(A)))
                        vect_ident_z.append(self.M*-1)

        EncaLate.append('Z')
        sizeMat = len(MatIde[len(MatIde) - 1])
        # print(Enca)
        for i in MatIde:
            difer = sizeMat - len(i)
            ceros_falta = '0' * difer
            list_ceros = list(ceros_falta)
            i = i + list_ceros  # Añadiendo los ceros faltantes
            MatrixIden.append(i)  # agregando a otra matriz
        MatrixIden.append(vect_ident_z)

        MatrizIdentNp = np.array(MatrixIden, dtype=str)
        ##agregando el Bi
        BiCol = self.modelData.get('dateBi')
        BiCol.append('0')
        BiColColumn = []
        for i in BiCol:
            BiColColumn.append([i])

        MatrizIdentBiNp = np.append(MatrizIdentNp, BiColColumn, axis=1)  # Agregando Columna
        print('Bi')
        MatrizIdenSym = []
        for line in MatrizIdentBiNp:
            # print(line)
            linea = []
            for elem in line:
                linea.append(sympify(elem))
            MatrizIdenSym.append(linea)
        # print(MatrizIdenSym)
        MatrizIdenSymNp = np.array(MatrizIdenSym)


        component_matrix = {'enca': Enca, 'encaLate': EncaLate, 'matrixIdent': MatrizIdenSymNp}
        return component_matrix

    def EncabezadoTop(self, enca, NunVar):
        Variables=['R/A']
        for x in range(NunVar):
            Variables.append(('X' + str(x + 1)))
        Variables.extend(enca)
        Variables.extend(['Bi'])
        return Variables

    def ModeloIterUno(self, MatrizRestrZ=None, MatrixIden=None):
        TablaModel = np.concatenate((MatrizRestrZ, MatrixIden), axis=1)
        tabla_model_list=[]

        for i in range(TablaModel.shape[0]):
            fila=[]
            for j in range(TablaModel.shape[1]):
                fila.append(sympify(TablaModel[i][j]))
            tabla_model_list.append(fila)
        tabla_model_np=np.array(tabla_model_list)


        return tabla_model_np

    def ModeloIterDos(self, enca, MatrizPlanteada):
        tipo=self.modelData['tipo']
        posM=[]
        VectSum=[]
        for i in range(len(enca)):
            var=enca[i]
            if var[0:(len(var)-1)]=='A':
                print(var[0:(len(var)-1)])
                posM.append(i)
        if len(posM)>0:
            for i in posM:
                VectSum.append(MatrizPlanteada[i,:])
            #print(VectSum)
            filas_sumadas_por_m=None
            if tipo=='Maximizar':
                filas_sumadas_por_m=np.sum(VectSum, axis=0)*self.M*-1
            elif tipo=='Minimizar':
                filas_sumadas_por_m = np.sum(VectSum, axis=0) *self.M
            MatrizPlanteadaClone = MatrizPlanteada.copy()
            MatrizPlanteadaClone[(len(MatrizPlanteadaClone)-1),:]=MatrizPlanteada[(len(MatrizPlanteada)-1),:]+filas_sumadas_por_m
            return MatrizPlanteadaClone

        return None

    def Iteraciones(self, matrizIter, tipo):
        MatrizModelo=matrizIter.copy()
        vectz=MatrizModelo[len(MatrizModelo)-1, :]#Vector >

        while self.verificar_nueva_iter(vectz, tipo):
            col_pv=self.col_pv(vectz, tipo)#Columna pivote
            print('Col pv: '+str(col_pv))
            vect_col_pv=MatrizModelo[:,col_pv]#Vector columna pivote
            vect_col_bi=MatrizModelo[:,(len(MatrizModelo[0])-1)]#Vector Bi
            row_pv=self.row_pv(vect_col_pv, vect_col_bi)#Fila pivote
            print(row_pv)
            print('row pv'+str(row_pv))

            val_div_row_pv=MatrizModelo[row_pv][col_pv]
            MatrizModelo[row_pv, :]=MatrizModelo[row_pv, :]/val_div_row_pv#Dividiendo entre toda la fila pivote
            for i in range(len(MatrizModelo)):
                val_mult_row_pv=MatrizModelo[i][col_pv]
                if i != row_pv:
                    MatrizModelo[i,:]=MatrizModelo[row_pv,:]*val_mult_row_pv*-1 + MatrizModelo[i,:]

            print(MatrizModelo)


        print("Llego aqui!! todo esta bien")

    def col_pv(self, vectz, tipo):
        pos=0
        if tipo=='Maximizar':
            menor = N(vectz[0].subs(self.M,1000))
            for i in range(len(vectz)-1):
                val_menor=N(vectz[i].subs(self.M,1000))
                if val_menor<menor:
                    menor=val_menor
                    pos=i
        elif tipo=='Minimizar':
            mayor = N(vectz[0].subs(self.M,1000))
            for i in range(len(vectz)-1):
                val_mayor=N(vectz[i].subs(self.M,1000))
                if val_mayor>mayor:
                    mayor=val_mayor
                    pos=i
        return pos


    def row_pv(self, vect_col_pv, vect_col_bi):
        pos=0
        print("hehehe")
        print(vect_col_pv)
        print(vect_col_bi)
        for i in range(len(vect_col_bi)-1):
            if N(vect_col_pv[i])!=0.0 and N(vect_col_pv[i])>0.0:
                coef_menor=N(vect_col_bi[i])/N(vect_col_pv[i])
                pos=i
                break
            else:
                pos=-1
        print(pos)
        for i in range(len(vect_col_bi)-1):
            if N(vect_col_pv[i])!=0.0 and N(vect_col_pv[i])>0.0:
                coef_val=N(vect_col_bi[i])/N(vect_col_pv[i])
                if coef_val<coef_menor:
                    coef_menor=coef_val
                    pos=i
        print(pos)
        return  pos

    def verificar_nueva_iter(self, vectz, tipo):
        res=False
        if tipo=='Maximizar':
            for i in range(len(vectz)-1):
                if N(vectz[i].subs(self.M,1000))<0:
                    res=True
                    break
        elif tipo=='Minimizar':
            for i in range(len(vectz)-1):
                if N(vectz[i].subs(self.M,1000))>0:
                    res=True
                    break

        return res









