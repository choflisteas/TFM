% STOPSILOP Detiene el procesamiento de las señales, así como las comunicaciones con los buses 
% y/o la simulación de los datosacuerdo a los IMUS y algoritmos indicados
%
% STOPSILOP Detiene el procesamiento de las señales, asi como las comunicaciones con los buses 
% y/o la simulacion de los datos de acuerdo a los IMUS y algoritmos indicados. En el caso de que se 
% esten generando logs, esta funcion crea los ficheros .sl definitivos.
% 
% Syntax: 
%   stopsilop(modo);
%
%   Parametros de entrada: 
%       Modo: indica si se debe detener totalmente el sistema (modo=1) o
%               solo la captura y procesamiento de datos (modo=0) en cuyo caso se podría 
%               reiniciar de nuevo con playsilop()
%   Parametros de salida: Ninguno
% 
% Examples: 
%   
%
% See also: 

% Author:   Diego Alvarez
% History:  29.01.2008  creado e Incorporado a la toolbox
%           12.02.2008  añadida la parte del Xbus por Rafa

function stopsilop(modo)

if (nargin<1)
    modo=0;
end

global SILOP_CONFIG
global SILOP_DATA_LOG; %#ok<NUSED>

if (isfield(SILOP_CONFIG,'File'))
    if (SILOP_CONFIG.File.Salvar>0)
        if (SILOP_CONFIG.File.Salvar==2)
            zip(SILOP_CONFIG.File.Name,{'config.mat','datos.log','datos_alg.log'});
            delete ('datos_alg.log');
        else
            zip(SILOP_CONFIG.File.Name,{'config.mat','datos.log'});
        end		
        delete ('config.mat');
        delete ('datos.log');
        movefile ([SILOP_CONFIG.File.Name,'.zip'], SILOP_CONFIG.File.Name, 'f');
    end
end

if (isstruct(SILOP_CONFIG.BUS))
    drivername=fieldnames(SILOP_CONFIG.BUS);
else
    drivername=[];
end
if (length(drivername)>1)
    error('solo se puede emplear un driver simultaneamente');
elseif (isempty(drivername))
    return;
else
    driverfunction=str2func(['driver_',drivername{1}]);
    try 
        SILOP_CONFIG.BUS.(drivername{1})=driverfunction('gotoconfig',SILOP_CONFIG.BUS.(drivername{1}));
    catch ME %#ok<NASGU>
       if (modo==0)
        modo=1; %La configuracion es errornea. No va a funcionar, así que necesitamos hacer destruye.
        disp('Error de comunicación. Se destruirá el driver antiguo antes de proseguir')
       end
    end
    if (modo>0)
         driverfunction('destruye',SILOP_CONFIG.BUS.(drivername{1}));
         SILOP_CONFIG.BUS=rmfield(SILOP_CONFIG.BUS,drivername{1});
    end
end



%Se limpian todos los algoritmos.
for indice=1:length(SILOP_CONFIG.ALGORITMOS)
     clear (SILOP_CONFIG.ALGORITMOS(indice).nombre)
end
