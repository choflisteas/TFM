% ADDALGORITMO Añade un algoritmo al sistema de procesamiento de las aplicaciones estandar de la toolbox
%
% ADDALGORITMO añade un algoritmo al sistema de procesamiento de las aplicaciones estandar de la toolbox. 
% No se pueden incluir algoritmos antes de realizar la conexión mediante connectsilop() ni después de 
% iniciarse el procesamiento con startsilop
% 
% Syntax: 
%   addalgoritmo(nombre, n_valores_retorno, senhales, params, dependencias)
%
%   Parámetros de entrada: 
%	nombre   -> Nombre del algoritmo a usar
%	n_valores_retorno -> Número de datos calculados por el algoritmo
%	senhales -> Nombre de las señales que va a emplear el algoritmo. Ej: COG.Acc_X
%	params  -> parametros de configuración del algoritmo
%	dependencias -> nombres de otros algoritmos, cuyos resultados son necesarios
%
%   Parámetros de salida: Ninguno
% 
% Examples: 
% addalgoritmo('alg_det_event', {'COG.HS','COG.TO'}, {'COG.Acc_Z', 'COG.Acc_X'}, [], {});
% addalgoritmo('alg_est_dist_pendulo' , {'COG.Dist'}, {'COG.Acc_Z','COG.HS'}, [], {});
% addalgoritmo('alg_est_orient_gyro', {'COG.Orient'}, {'COG.G_Z'}, [], {});
% addalgoritmo('alg_est_2d', {'COG.X','COG.Y'}, {'COG.Dist','COG.Orient'}, [], {});
% addalgoritmo('alg_plot_pos2d', 1, {'COG.X','COG.Y'}, [], {});
%   
% See also: 

% Author:   Antonio López
% History:  24.01.2008  creado
%           25.01.2008 Incorporado a la toolbox
%           01.02.2008 se busca con buscaposiciones{k} y no de {l}. Necesario para dependencias multiples   

function addalgoritmo(nombre, retornos, senhales, params, dependencias)

    global SILOP_CONFIG;
    
    alg.senhales=[];
    if (~isempty(senhales))
        if (~iscell(senhales))
            error('la lista de señales debe ser un cell array')
        end
        for senhal=senhales
            [punto,dato]=strtok(senhal{1},'.'); %Rompo por el punto
            dato=dato(2:end); %Quito el punto
            if (~isfield(SILOP_CONFIG.SENHALES,punto))
                error('No existe el punto %s especificado',punto);
            end
            if (~isfield(SILOP_CONFIG.SENHALES.(punto),dato))
                error('No existe el dato %s solicitado en %s',dato,punto);
            end
            alg.senhales=[alg.senhales SILOP_CONFIG.SENHALES.(punto).(dato)];
        end
    end

    alg.parametros = params;    
    
    %Punto en el que se insertaran las señales nuevas
    col_disp = SILOP_CONFIG.GLOBAL.COLUMNADISPONIBLE;
    if(col_disp == -1)
        col_disp = SILOP_CONFIG.SENHALES.NUMEROSENHALES+1;
    end;
    
    
    if (isnumeric(retornos))
        n_valores_retorno=retornos;
    else 
        n_valores_retorno=0;
        if (~isempty(retornos))
            if (~iscell(retornos))
                error('la lista de señales retornadas debe ser un cell array')
            end
            for senhal=retornos
                [punto,dato]=strtok(senhal{1},'.'); %Rompo por el punto
                dato=dato(2:end); %Quito el punto
                if (isfield(SILOP_CONFIG.SENHALES,punto))
                    if (isfield(SILOP_CONFIG.SENHALES.(punto),dato))
                       error('La señal %s del %s ya existe',dato,punto);
                    end
                end
                n_valores_retorno=n_valores_retorno+1;
            end
            indice=0;
            for senhal=retornos
                [punto,dato]=strtok(senhal{1},'.'); %Rompo por el punto
                dato=dato(2:end); %Quito el punto
                SILOP_CONFIG.SENHALES.(punto).(dato)=col_disp+indice;
                disp(['Anadida senhal ',punto,'.',dato]); 
            
                SILOP_CONFIG.SENHALES.NUMEROSENHALES=SILOP_CONFIG.SENHALES.NUMEROSENHALES+1;
                indice=indice+1;
            end
        end
    end
    
    
    %Muevo esto al final, hasta que ya se que los datos están bien
    alg.posiciones = col_disp:col_disp+n_valores_retorno-1;
    SILOP_CONFIG.GLOBAL.COLUMNADISPONIBLE = col_disp+n_valores_retorno;
    
    alg.nombre = nombre;
    
    
    SILOP_CONFIG.ALGORITMOS = [SILOP_CONFIG.ALGORITMOS alg];

