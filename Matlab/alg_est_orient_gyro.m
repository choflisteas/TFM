%ALG_EST_ORIENT_GYRO Algoritmo para la estimacion de la orientaci�n mediante el gir�scopo
%
%ALG_EST_ORIENT_GYRO Algoritmo para la estimacion de la orientaci�n mediante el gir�scopo. 
% Este algoritmo actua como wrapper de la funcion orientaciongiroscopo.
%Se puede configurar mediante:
%    addalgoritmo('alg_est_orient_gyro', {'COG.Orient'}, {'COG.G_Z'}, []);
%
%Parametros: como todos los alg_ resultados anteriores, se�ales a usar, parametros(se puede indicar 
% unicamente la frecuencia de muestreo)

%Creado: 01-02-2008 por Diego

function resultado = alg_est_orient_gyro(previos, senhales, params) %#ok<INUSD>

        giro = senhales;
	resultado = previos;
        
        mov_sin_calcular = find(isnan(resultado)); %Filas aun no procesadas
	if (~isempty(mov_sin_calcular))
        
	if (isempty(params))
		resultado(mov_sin_calcular)=orientaciongiroscopo(giro(mov_sin_calcular));        
    else
        resultado(mov_sin_calcular)=orientaciongiroscopo(giro(mov_sin_calcular),giro(mov_sin_calcular(1)-1),params); 
	end       
	end
        

