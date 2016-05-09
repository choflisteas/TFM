% CONNECTSILOP Conecta el sistema de procesamiento con los sensores previamente especificados
%
% CONNECTSILOP Conecta el sistema de procesamiento con los sensores
% previamente especificados, o en el caso de trabajar
% en modo simulacion con el fichero en el que esta guardado un log
% capturado
% 
% Syntax: 
%   connectsilop(driver, source, freq, updateeach, driver_opt)
%
%   Parametros de entrada:
%		driver:  Cadena de texto que indica el modo de funcionamiento (nombre
%               del driver a usar). Por ejemplo: 
%               'Xbus':             sensor xbus (por defecto)
%               'Temporizador':     modo de simulacion
%               'SF_3D':            SparkFun 3D serial accelerometer
%                ...:               Consultar la lista de drivers en la
%                                   documentacion para ver otros dispositivos soportados
%       source     Puerto y/o fichero del que leer los datos
%                        Valor por defecto: 'COM24'
%                           El puerto de comunicaciones será tipicamente
%                           COMx en windows o /dev/ttyUSBX en linux
%                        El fichero para la simulacion  puede se un .log de Xsens, un .tana de Xsens
%			             calibrado, o un .sl de la propia toolbox
%		freq       Frecuencia de muestreo solicitada. Puede no coincidir con la real.
%                   100Hz por defecto
%       updateeach Tiempo tras el cual se realizará el procesamiento de los
%                   datos recibidos. Por defecto 1 segundo.
%       driver_opt Parametros especificos para cada driver, que se deben
%                   consultar en la documentacion del mismo.
%
%   Parametros de salida: Ninguno 
% 
% Examples: 
%   
%
% See also: 


function connectsilop(driver, source, freq, updateeach, driver_opt)
    
   if (nargin<1)
        driver='Xbus';
    end	
    if (nargin<2)
        source='COM24';
    end
    if (nargin<3)
        freq=100;
    end
    if (nargin<4)
        updateeach=1;
    end
    if (nargin<5)
        driver_opt=[];
    end
    global SILOP_DATA_BUFFER;
    SILOP_DATA_BUFFER = [];
    global SILOP_CONFIG;
    
    %Comprobamos si existen señales
    posiciones=fieldnames(SILOP_CONFIG.SENHALES);
    numerodeimus=length(posiciones)-1;
    if (numerodeimus==0)
        error('no se ha indicado ningún IMU mediante addimu');
    end
    
    funcionnecesaria=@driver_Xbus;%Para que se compile al usar mcc
    driverfunction=str2func(['driver_',driver]);
    try
        SILOP_CONFIG.BUS.(driver)=driverfunction('create',{source,freq,updateeach,numerodeimus,driver_opt});
    catch ME
        if (strcmp(ME.identifier,'MATLAB:UndefinedFunction'))
            disp('El driver seleccionado no está disponible');
        end
        rethrow(ME);
    end
    try
        SILOP_CONFIG.BUS.(driver) = driverfunction('connect',SILOP_CONFIG.BUS.(driver));
        SILOP_CONFIG.BUS.(driver) = driverfunction('gotoconfig',SILOP_CONFIG.BUS.(driver));
        [SILOP_CONFIG.BUS.(driver),SILOP_CONFIG.SENHALES] = driverfunction('configura',{SILOP_CONFIG.BUS.(driver),SILOP_CONFIG.SENHALES});
    catch ME
        disp (ME.message);
        driverfunction('destruye',SILOP_CONFIG.BUS.(driver));
        SILOP_CONFIG.BUS=rmfield(SILOP_CONFIG.BUS,driver);
        rethrow(ME);
    end
