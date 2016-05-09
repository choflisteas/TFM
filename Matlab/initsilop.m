% INITSILOP Inicializa el sistema de procesamiento de las aplicaciones estandar de la toolbox
%
% INITSILOP Inicializa el sistema de procesamiento de las aplicaciones estandar de la toolbox. 
% Debe ser el primer comando usado en dichas aplicaciones.
% 
% Syntax: 
%   initsilop();
%
%   Parámetros de entrada: Ninguno
%   Parámetros de salida: Ninguno
% 
% Examples: 
%   
%
% See also: 

% Author:   Antonio López
% History:  24.01.2008  creado
%           24.01.2008 Incorporado a la toolbox
%


function initsilop()

global SILOP_CONFIG
if (~isempty(SILOP_CONFIG))
    if (isfield(SILOP_CONFIG,'File'))
    	SILOP_CONFIG.File.Salvar=0;
    end
    stopsilop(1);
	SILOP_CONFIG=[];
end

%Tamaño de la ventana de datos
SILOP_CONFIG.GLOBAL.LONGITUDVENTANA = 1000;

%Números de serie y señales iniciales de todos los posibles sensores que se pueden usar
SILOP_CONFIG.SENHALES=[];
SILOP_CONFIG.SENHALES.NUMEROSENHALES = 0;

%Datos generales del bus
SILOP_CONFIG.BUS=[];

%Datos de los algoritmos usados
SILOP_CONFIG.ALGORITMOS = [];
SILOP_CONFIG.GLOBAL.COLUMNADISPONIBLE = -1;
