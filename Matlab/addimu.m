% ADDIMU AÃ±ade un IMU al sistema de procesamiento de las aplicaciones estandar de la toolbox
%
% ADDIMU aÃ±ade un IMU al sistema de procesamiento de las aplicaciones estandar de la toolbox. 
% Se debe incluir la lista completa de IMUs a usar antes de realizar la conexion
% 
% Syntax: 
%   addimu(posicion,numserie, orientacion, userdata);
%
%   Parametros de entrada: 
%	posicion -> Cadena de texto conteniendo la posicion en la que esta el sensor.
%	numserie -> numero de serie
%   orientacion -> Vector de tres elementos que debe indicar cual es la direccion antero-posterior,
%                   medio-lateral y vertical referida a los ejes del acelerometro. X=1,Y=2,Z=3.
%                   Por defecto vale [3,-2,1] en el COG=[antero-posterior=Z del acelerometro, Medio-lateral=-Y del
%                   acelerometro, vertical=X del acelerometro].
%                   En el resto de puntos es [1,2,3], o lo que es lo mismo, no se reorientan por defecto.
%		    Se aceptan valores negativos para indicar que el eje anatomico y el del acelerometro son opuestos.
%   userdata -> Parámetro con información adicional proporcionada por el
%               usuario. Ejemplo, masa asociada al sensor
%	            
%   Parametros de salida: Ninguno
% 
% Examples: 
%   
%
% See also: 

% Author:   Antonio Lopez
% History:  24.01.2008  creado
%           24.01.2008 Incorporado a la toolbox
%

function addimu(donde, serie, R, userdata) %#ok<INUSD>
	global SILOP_CONFIG;
	
    if (nargin<2)
		error('es necesario especificar los dos primeros parï¿½metros');
	elseif (nargin<3)
        if(strcmp(donde,'COG'))
			R=[3,-2,1]; 
        else
            R=[1,2,3];
        end
    elseif (nargin<4)
        userdata=[];
    end

    posiciones=fieldnames(SILOP_CONFIG.SENHALES);
    if (~isempty(strmatch(donde, posiciones,'exact'))) %#ok<MATCH3>
         error('el sensor ya estaba declarado')
    end
    SILOP_CONFIG.SENHALES.(donde).Serie=serie;
	SILOP_CONFIG.SENHALES.(donde).R=R;
    SILOP_CONFIG.SENHALES.(donde).userdata=userdata;

