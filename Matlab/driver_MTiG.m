% driver_MTiG implementa todo el código necesario para el correcto funcionamiento
% del dispositivo XSens MTi-G .
% No está pensado para llamarse por si mismo, sino para ser usado desde el
% sistema de captura de la toolbox.
%
%
% driver_MTiG implementa todo el código necesario para el correcto funcionamiento
% del dispositivo XSens MTi-G .
% No está pensado para llamarse por si mismo, sino para ser usado desde el
% sistema de captura de la toolbox.
%
% Se definen 6 modos de funcionamiento en función de las señales que 
% son procesadas y devueltas por el driver:
%
%       . 0: datos calibrados  
%       . 1: calibrados y orientados (cuaternas)
%       . 2: calibrados y orientados (euler)
%       . 3: calibrados y orientados (matrix)
%
%       .4: Posición(LLA) + Veloidad + Status (del GPS) 
%       .5: Calibrados+ Posición(LLA) + Velocidad + Status (del GPS)
%       .6: RAW Inertial+GPS 
%
% (los cuatro primeros son análogos a los usados por el XBusMaster y los dispositivos MTx,
%   los tres últimos específicos del MTi-G)
%
% NOTA: La selección de modo se realiza a través del quinto parámetro 
%       de entrada de la función connectsilop: driver_opt
%               connectsilop(driver, source, freq, updateeach, driver_opt);
%                                                                driver_opt=[bps modo];
%
%       Asimismo para seleccionar este driver como primer parámetro de
%       entrada de la función connectsilop (driver) hemos de indicarle:
%       MTiG 
%
%
% Syntax: retorno=driver_MTiG(operacion, parametros)
% 
% Output parameters:
%
% Examples:

function [retorno,senhales]=driver_MTiG(operacion,parametros)
    senhales=[];
    switch operacion
        case 'create'
            retorno=creaMTiG(parametros);
        case 'connect'
            retorno=connectMTiG(parametros);
        case 'configura'
            [retorno,senhales]=configuraMTiG(parametros);
        case 'gotoconfig'
            retorno=gotoconfig(parametros);
        case 'gotomeasurement'
            retorno=gotomeasurement(parametros);
        case 'destruye'
            retorno=[];
            destruyeMTiG(parametros);
        otherwise
            disp('error, el driver no soporta la operaciÃ³n indicada');
            retorno=[];
    end
end

function MTiG=creaMTiG(parametros)
    source=parametros{1};
    freq=parametros{2};
    updateeach=parametros{3};
    driver_opt=parametros{5};
    if (length(driver_opt)<1)
        bps=460800;    
    else
         bps=driver_opt(1);
    end
    if (length(driver_opt)<2)
        modo=0;
    else
        modo=driver_opt(2);
    end
    % Calculamos el numero de muestras almacenadas en el buffer
    MTiG.freq=freq;
    MTiG.buffer=updateeach*freq;
    
    try
        MTiG.puerto=serial(source);
    catch ME
        disp ('Imposible conectarse al puerto serie');
        rethrow (ME);
    end
    MTiG.modo=modo;
    
    switch (MTiG.modo)
        case 0,                     % cal                                  
            MTiG.DataLength=36+2; 
            MTiG.Data=1+9;
        case 1,                     % cal+ cuat
            MTiG.DataLength=36+16+2;
            MTiG.Data=1+9+4;
        case 2,                     % cal+ euler
            MTiG.DataLength=36+12+2;
            MTiG.Data=1+9+3;
        case 3,                     % cal+ mat
            MTiG.DataLength=36+36+2;
            MTiG.Data=1+9+9;
        case 4,                     % LLA+Vel+St
            MTiG.DataLength=12+12+1+2;
            MTiG.Data=1+3+3+1;
        case 5,                     % cal + LLA+Vel+St
            MTiG.DataLength=36+12+12+1+2;
            MTiG.Data=1+9+3+3+1;
        case 6,                     % Raw inertial + gps
          MTiG.DataLength= 20+44+2;
          MTiG.Data=1+10+13;
        otherwise,
            disp ('modo invalido');
            delete (MTiG.puerto);
						error ('Modo invalido')
    end;
    if (MTiG.DataLength>254)
        MTiG.DataLength=MTiG.DataLength+7; % se incluye la cabecera y el checksum
    else
        MTiG.DataLength=MTiG.DataLength+5; % Se incluye la cabecera y el checksum
    end

    MTiG.bps=bps;
end

function MTiG=connectMTiG(parametros)
    MTiG=parametros;
    % Configurar el objeto serie
    MTiG.puerto.BaudRate=MTiG.bps;
    MTiG.puerto.DataBits=8;
    MTiG.puerto.FlowControl='none';
    MTiG.puerto.Parity='none';
    MTiG.puerto.StopBits=2;
    MTiG.puerto.ReadAsyncMode = 'continuous';
    MTiG.puerto.ByteOrder = 'littleEndian';
    MTiG.puerto.BytesAvailableFcnCount = MTiG.DataLength*MTiG.buffer;
    MTiG.puerto.BytesAvailableFcnMode = 'byte';
    MTiG.puerto.InputBufferSize = MTiG.DataLength*300;
    MTiG.puerto.OutputBufferSize = 512;
    MTiG.puerto.Tag = 'MTiG';
    MTiG.puerto.DataTerminalReady='off';
    MTiG.puerto.Timeout = 10;
    % Abrir el puerto de comunicaciones
    fopen(MTiG.puerto);
    
%     % 9/10/2008: Pruebas de la Toolbox
%     % Activar la grabacion de la actividad del puerto
%     % 9/10/2008
%     xbus.puerto.RecordMode='index';
%     xbus.puerto.RecordDetail='compact';
%     xbus.puerto.RecordName='Pruebas1.txt';
%     record(xbus.puerto);
    
end

function [MTiG,senhales]=configuraMTiG(parametros)

    MTiG=parametros{1};
    senhales=parametros{2};
    MTiG=SetPeriod(MTiG,MTiG.freq);
    switch (MTiG.modo)
        case 0,
            MTiG=SetMTOutputMode(MTiG,0);
        case 1,
            MTiG=SetMTOutputMode(MTiG,1);
        case 2,
            MTiG=SetMTOutputMode(MTiG,2);
        case 3,
            MTiG=SetMTOutputMode(MTiG,3);
        case 4,
            MTiG=SetMTOutputMode(MTiG,4);
        case 5,
            MTiG=SetMTOutputMode(MTiG,5);
        case 6,
            MTiG=SetMTOutputMode(MTiG,6);
    end    
    
    % Actualizar los valores de las seï¿½ales
    
    % NOTA: Factor va a depender del tamaño del campo Data del msg MTData 
        % ed, tiene el mismo valor
               
    switch (MTiG.modo)        
        case 0,         % cal
            factor=9;                           %#ok<NASGU>
        case 1,         % cal+ cuat
            factor=9+4;                         %#ok<NASGU>
        case 2,         % cal+ eul
            factor=9+3;                         %#ok<NASGU>
        case 3,         % cal+ mat
            factor=9+9;                         %#ok<NASGU>            
        case 4,         % LLA +Vel +St
            factor=3+3+1;                       %#ok<NASGU>                      
        case 5,         % cal +LLA +Vel +St
            factor=9+3+3+1;                     %#ok<NASGU>
        case 6,         % RAW in+gps
            factor=1+10+13;                     %#ok<NASGU>
    end; 
   
    
    posiciones=fieldnames(senhales);   %Dve un vector d celdas con cadenas 
            % d caracteres q recogen los nombres dlos campos la estructura senhales

    orden=senhales.(posiciones{2}).R;
    Rot=zeros(3,3);
    for k=1:3  
        Rot(k,abs(orden(k)))=sign(orden(k));
    end;
            
    SetObjectAlignment(MTiG,1,Rot);
    
    switch (MTiG.modo)
       case 0,     % cal
            senhales.(posiciones{2}).Acc_Z = 4;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Z']); 
            senhales.(posiciones{2}).Acc_Y = 3;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Y']); 
            senhales.(posiciones{2}).Acc_X = 2;
            disp(['Anadida senhal ',posiciones{2},'.Acc_X']); 
            senhales.(posiciones{2}).G_Z = 7;
            disp(['Anadida senhal ',posiciones{2},'.G_Z']); 
            senhales.(posiciones{2}).G_Y = 6;
            disp(['Anadida senhal ',posiciones{2},'.G_Y']); 
            senhales.(posiciones{2}).G_X = 5;
            disp(['Anadida senhal ',posiciones{2},'.G_X']); 
            senhales.(posiciones{2}).MG_Z = 10;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            senhales.(posiciones{2}).MG_Y = 9;
            disp(['Anadida senhal ',posiciones{2},'.MG_Y']); 
            senhales.(posiciones{2}).MG_X = 8;
            disp(['Anadida senhal ',posiciones{2},'.MG_X']);     %#ok<NASGU>
            
       case 1,     % cal +cuat  
            senhales.(posiciones{2}).Acc_Z = 4;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Z']); 
            senhales.(posiciones{2}).Acc_Y = 3;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Y']); 
            senhales.(posiciones{2}).Acc_X = 2;
            disp(['Anadida senhal ',posiciones{2},'.Acc_X']); 
            senhales.(posiciones{2}).G_Z = 7;
            disp(['Anadida senhal ',posiciones{2},'.G_Z']); 
            senhales.(posiciones{2}).G_Y = 6;
            disp(['Anadida senhal ',posiciones{2},'.G_Y']); 
            senhales.(posiciones{2}).G_X = 5;
            disp(['Anadida senhal ',posiciones{2},'.G_X']); 
            senhales.(posiciones{2}).MG_Z = 10;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            senhales.(posiciones{2}).MG_Y = 9;
            disp(['Anadida senhal ',posiciones{2},'.MG_Y']); 
            senhales.(posiciones{2}).MG_X = 8;
            disp(['Anadida senhal ',posiciones{2},'.MG_X']); 
            
            senhales.(posiciones{2}).Q_I = 11;
            disp(['Anadida senhal ',posiciones{2},'.Q_I']); 
            senhales.(posiciones{2}).Q_II = 12;
            disp(['Anadida senhal ',posiciones{2},'.Q_II']);
            senhales.(posiciones{2}).Q_III = 13;
            disp(['Anadida senhal ',posiciones{2},'.Q_III']);
            senhales.(posiciones{2}).Q_IV = 14;
            disp(['Anadida senhal ',posiciones{2},'.Q_IV']);    %#ok<NASGU>
            
       case 2,     % cal +eul 
            senhales.(posiciones{2}).Acc_Z = 4;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Z']); 
            senhales.(posiciones{2}).Acc_Y = 3;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Y']); 
            senhales.(posiciones{2}).Acc_X = 2;
            disp(['Anadida senhal ',posiciones{2},'.Acc_X']); 
            senhales.(posiciones{2}).G_Z = 7;
            disp(['Anadida senhal ',posiciones{2},'.G_Z']); 
            senhales.(posiciones{2}).G_Y = 6;
            disp(['Anadida senhal ',posiciones{2},'.G_Y']); 
            senhales.(posiciones{2}).G_X = 5;
            disp(['Anadida senhal ',posiciones{2},'.G_X']); 
            senhales.(posiciones{2}).MG_Z = 10;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            senhales.(posiciones{2}).MG_Y = 9;
            disp(['Anadida senhal ',posiciones{2},'.MG_Y']); 
            senhales.(posiciones{2}).MG_X = 8;
            disp(['Anadida senhal ',posiciones{2},'.MG_X']); 
            
            senhales.(posiciones{2}).Roll = 11;
            disp(['Anadida senhal ',posiciones{2},'.Roll']); 
            senhales.(posiciones{2}).Pitch = 12;
            disp(['Anadida senhal ',posiciones{2},'.Pitch']);
            senhales.(posiciones{2}).Yaw = 13;
            disp(['Anadida senhal ',posiciones{2},'.Yaw']);    %#ok<NASGU>
            
       case 3,     % cal +mat
            senhales.(posiciones{2}).Acc_Z = 4;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Z']); 
            senhales.(posiciones{2}).Acc_Y = 3;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Y']); 
            senhales.(posiciones{2}).Acc_X = 2;
            disp(['Anadida senhal ',posiciones{2},'.Acc_X']); 
            senhales.(posiciones{2}).G_Z = 7;
            disp(['Anadida senhal ',posiciones{2},'.G_Z']); 
            senhales.(posiciones{2}).G_Y = 6;
            disp(['Anadida senhal ',posiciones{2},'.G_Y']); 
            senhales.(posiciones{2}).G_X = 5;
            disp(['Anadida senhal ',posiciones{2},'.G_X']); 
            senhales.(posiciones{2}).MG_Z = 10;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            senhales.(posiciones{2}).MG_Y = 9;
            disp(['Anadida senhal ',posiciones{2},'.MG_Y']); 
            senhales.(posiciones{2}).MG_X = 8;
            disp(['Anadida senhal ',posiciones{2},'.MG_X']); 
            
            senhales.(posiciones{2}).A = 11;
            disp(['Anadida senhal ',posiciones{2},'.A']); 
            senhales.(posiciones{2}).B = 12;
            disp(['Anadida senhal ',posiciones{2},'.B']);
            senhales.(posiciones{2}).C = 13;
            disp(['Anadida senhal ',posiciones{2},'.C']);
            senhales.(posiciones{2}).D = 14;
            disp(['Anadida senhal ',posiciones{2},'.D']);
            senhales.(posiciones{2}).E = 15;
            disp(['Anadida senhal ',posiciones{2},'.E']);
            senhales.(posiciones{2}).F = 16;
            disp(['Anadida senhal ',posiciones{2},'.F']);
            senhales.(posiciones{2}).G = 17;
            disp(['Anadida senhal ',posiciones{2},'.G']);
            senhales.(posiciones{2}).H = 18;
            disp(['Anadida senhal ',posiciones{2},'.H']);
            senhales.(posiciones{2}).I = 19;
            disp(['Anadida senhal ',posiciones{2},'.I']);    %#ok<NASGU>
            
       case 4,     %LLA +vel +stat
            % 12/11/2008 Añado los campos para las nuevas variables de los 
            % nuevos modos Lat,Long,Alt,Vel_X,Vel_Y,Vel_Z
            senhales.(posiciones{2}).Lat = 2;
            disp(['Anadida senhal ',posiciones{2},'.Lat']); 
            senhales.(posiciones{2}).Long = 3;
            disp(['Anadida senhal ',posiciones{2},'.Long']);
            senhales.(posiciones{2}).Alt = 4;
            disp(['Anadida senhal ',posiciones{2},'.Alt']);
            senhales.(posiciones{2}).Vel_X = 5;
            disp(['Anadida senhal ',posiciones{2},'.Vel_X']);
            senhales.(posiciones{2}).Vel_Y = 6;
            disp(['Anadida senhal ',posiciones{2},'.Vel_Y']);
            senhales.(posiciones{2}).Vel_Z = 7;
            disp(['Anadida senhal ',posiciones{2},'.Vel_Z']);       
            senhales.(posiciones{2}).Status = 8;
            disp(['Anadida senhal ',posiciones{2},'.Status']);     %#ok<NASGU>
                                 
       case 5,     % cal +LLA +vel +stat
            senhales.(posiciones{2}).Acc_Z = 4;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Z']); 
            senhales.(posiciones{2}).Acc_Y = 3;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Y']); 
            senhales.(posiciones{2}).Acc_X = 2;
            disp(['Anadida senhal ',posiciones{2},'.Acc_X']); 
            senhales.(posiciones{2}).G_Z = 7;
            disp(['Anadida senhal ',posiciones{2},'.G_Z']); 
            senhales.(posiciones{2}).G_Y = 6;
            disp(['Anadida senhal ',posiciones{2},'.G_Y']); 
            senhales.(posiciones{2}).G_X = 5;
            disp(['Anadida senhal ',posiciones{2},'.G_X']); 
            senhales.(posiciones{2}).MG_Z = 10;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            senhales.(posiciones{2}).MG_Y = 9;
            disp(['Anadida senhal ',posiciones{2},'.MG_Y']); 
            senhales.(posiciones{2}).MG_X = 8;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            
            senhales.(posiciones{2}).Lat = 11;
            disp(['Anadida senhal ',posiciones{2},'.Lat']); 
            senhales.(posiciones{2}).Long = 12;
            disp(['Anadida senhal ',posiciones{2},'.Long']);
            senhales.(posiciones{2}).Alt = 13;
            disp(['Anadida senhal ',posiciones{2},'.Alt']);
            senhales.(posiciones{2}).Vel_X = 14;
            disp(['Anadida senhal ',posiciones{2},'.Vel_X']);
            senhales.(posiciones{2}).Vel_Y = 15;
            disp(['Anadida senhal ',posiciones{2},'.Vel_Y']);
            senhales.(posiciones{2}).Vel_Z = 16;
            disp(['Anadida senhal ',posiciones{2},'.Vel_Z']);
            senhales.(posiciones{2}).Status = 17;
            disp(['Anadida senhal ',posiciones{2},'.Status']);      %#ok<NASGU>
                 
       case 6,     %RAW Inercial + GPS
            senhales.(posiciones{2}).Acc_Z = 4;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Z']); 
            senhales.(posiciones{2}).Acc_Y = 3;
            disp(['Anadida senhal ',posiciones{2},'.Acc_Y']); 
            senhales.(posiciones{2}).Acc_X = 2;
            disp(['Anadida senhal ',posiciones{2},'.Acc_X']); 
            senhales.(posiciones{2}).G_Z = 7;
            disp(['Anadida senhal ',posiciones{2},'.G_Z']); 
            senhales.(posiciones{2}).G_Y = 6;
            disp(['Anadida senhal ',posiciones{2},'.G_Y']); 
            senhales.(posiciones{2}).G_X = 5;
            disp(['Anadida senhal ',posiciones{2},'.G_X']); 
            senhales.(posiciones{2}).MG_Z = 10;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            senhales.(posiciones{2}).MG_Y = 9;
            disp(['Anadida senhal ',posiciones{2},'.MG_Y']); 
            senhales.(posiciones{2}).MG_X = 8;
            disp(['Anadida senhal ',posiciones{2},'.MG_Z']); 
            
            senhales.(posiciones{2}).Temp = 11;
            disp(['Anadida senhal ',posiciones{2},'.Temp']); 
            senhales.(posiciones{2}).Press = 12;
            disp(['Anadida senhal ',posiciones{2},'.Press']);
            senhales.(posiciones{2}).bPrs = 13;
            disp(['Anadida senhal ',posiciones{2},'.bPrs']);
            senhales.(posiciones{2}).ITOW = 14;
            disp(['Anadida senhal ',posiciones{2},'.ITOW']);
            senhales.(posiciones{2}).LAT = 15;
            disp(['Anadida senhal ',posiciones{2},'.LAT']);
            senhales.(posiciones{2}).LONG = 16;
            disp(['Anadida senhal ',posiciones{2},'.LONG']);
            senhales.(posiciones{2}).ALT = 17;
            disp(['Anadida senhal ',posiciones{2},'.ALT']);
            senhales.(posiciones{2}).VELE = 18;
            disp(['Anadida senhal ',posiciones{2},'.VELE']);
            senhales.(posiciones{2}).VELN = 19;
            disp(['Anadida senhal ',posiciones{2},'.VELN']);
            senhales.(posiciones{2}).VELD = 20;
            disp(['Anadida senhal ',posiciones{2},'.VELD']);
            senhales.(posiciones{2}).Hacc = 21;
            disp(['Anadida senhal ',posiciones{2},'.Hacc']);
            senhales.(posiciones{2}).Vacc = 22;
            disp(['Anadida senhal ',posiciones{2},'.Vacc']);
            senhales.(posiciones{2}).bGPS = 23;
            disp(['Anadida senhal ',posiciones{2},'.bGPS']);      %#ok<NASGU>
           
    end; 
 
end

function MTiG=destruyeMTiG(MTiG)

    try 
        fclose(MTiG.puerto);
    catch %#ok<CTCH>
    end
    delete(MTiG.puerto);
    clear MTiG
    MTiG=[];
end

function MTiG=gotoconfig(MTiG)

    % Envia el mensaje GoToConfig al objeto MTiG
    % Cuerpo del mensaje (excepto el byte de checksum) gotoconfig ###
    msg=[250,255,48,0];
    % Se calcula el cheksum y se coloca al final
    msg=[msg 256-mod(sum(msg(2:end)),256)];
    % Se envia por el puerto serie 
    fwrite(MTiG.puerto,msg,'uint8','async');

    %Ya deberiamos estar en modo config.
    %Permitimos comunicaciones
    MTiG.puerto.RequestToSend='on';
    %y damos tiempo a que se termine cualquier trasmision en curso
    pause(1);

    %Limpiamos todo lo que puede quedar en el buffer de medidas anteriores
    MTiG.puerto.Timeout=10;
    while (MTiG.puerto.BytesAvailable>0)
        disp(['>>> AVISO: Se descartaran ' int2str(MTiG.puerto.BytesAvailable) ' datos']);
        fread(MTiG.puerto,MTiG.puerto.BytesAvailable,'uint8');
    end

    %Reenviamos el mensaje y esta vez comprobamos la respuesta.
    fwrite(MTiG.puerto,msg,'uint8','async');
    % Se espera a recibir la contestacion
    [ack,cnt,msg]=fread(MTiG.puerto,5,'uint8');
    if (~isempty(msg))
        error('no se ha recibido la respuesta al comando gotoconfig');
    else
        if (mod(sum(ack(2:end)),256)~=0)
            error('Error de checksum durante gotoconfig');
        else
            if (ack(3)~=49)
                error ('mensaje incorrecto recibido durante gotoconfig');
            end
        end
    end
end

%Funcion para el paso a modo medida
function MTiG=gotomeasurement(MTiG)
    global SILOP_DATA_BUFFER;
    SILOP_DATA_BUFFER=[];

    % Cuerpo del mensaje (excepto el byte de checksum) gotomeasurement ###
    msg=[250,255,16,0];
    % Se calcula el cheksum y se coloca al final
    msg=[msg 256-mod(sum(msg(2:end)),256)];
    % Se envia por el puerto serie 
    if (MTiG.puerto.BytesAvailable>0)
        % Vaciar el puerto 
        % OJO!!! Los datos se perderan
        disp(['>>> AVISO: Se descartaran ' int2str(MTiG.puerto.BytesAvailable) ' datos']);
        fread(MTiG.puerto, MTiG.puerto.BytesAvailable,'uint8');
    end
    % El valor del TimeOut se fija a 1 segundo
    MTiG.puerto.Timeout=1;
    fwrite(MTiG.puerto,msg,'uint8');
    % Se espera a recibir la contestacion
    [ack,cnt,msg]=fread(MTiG.puerto,5,'uint8');
    if (~isempty(msg))
        disp(msg);
        error('no se ha recibido respuesta al mensaje gotomeasurement');
    elseif (mod(sum(ack(2:end)),256)~=0)
        error('Error de checksum durante el comando gotomeasurement');
    elseif (ack(3)~=17)
                error('Error en la secuencia de mensajes durante el comando gotomeasurement');
    end
    MTiG.puerto.RequestToSend='off'; % 9/10/2008
    leerMTiGDatahandle=@leerMTiGData;
    MTiG.puerto.BytesAvailableFcn={leerMTiGDatahandle, MTiG};
    MTiG.puerto.RequestToSend='on'; % 9/10/2008
end


% LEERMTiGDATA Lee datos desde el dispositivo MTiG
% Lee datos del buffer. Llamada por una callback
function leerMTiGData(obj,event,MTiG)            %#ok<INUSL>
    global SILOP_DATA_BUFFER;
    
    data=fread(obj,[MTiG.DataLength MTiG.buffer],'uint8');
       
    % Procesar los datos de 1 mensaje
    % checksum
    if (any(mod(sum(data(2:end,:)),256)) )
        disp('>>>> ERROR de checksum durante la captura de datos');
    end
    %tipo de mensaje
    if (any(data(3,:)-50))
        disp('>>>> ERROR de tipo de mensaje durante la captura de datos');
    end
    
    % procesar la informacion
     q=quantizer('Mode','single');
    SILOP_DATA_BUFFER=[]; 
    
    %     OJO!!
%     Trabajando con el XBusMaster y los sensores MTx 
%     el  nº de muestras lo coloca en los campos 5 y 6
%      (al principio del campo MTData del msg)
%
%     Con el sensor MTi-G lo coloca en los campos 41 y 42
%      (al final del campo MTData del msg)

%    --> hay que cambiar los índices de data (donde se almacena la
%    lectura del puerto) -- Se "adelantan" dos
    
  switch (MTiG.modo)
      case 0     % cal
        ax=hex2num(q,reshape(sprintf('%02X',data((5:8),:)),[8 MTiG.buffer])'); 
        ay=hex2num(q,reshape(sprintf('%02X',data((9:12),:)),[8 MTiG.buffer])'); 
        az=hex2num(q,reshape(sprintf('%02X',data((13:16),:)),[8 MTiG.buffer])'); 
        rx=hex2num(q,reshape(sprintf('%02X',data((17:20),:)),[8 MTiG.buffer])'); 
        ry=hex2num(q,reshape(sprintf('%02X',data((21:24),:)),[8 MTiG.buffer])'); 
        rz=hex2num(q,reshape(sprintf('%02X',data((25:28),:)),[8 MTiG.buffer])'); 
        mx=hex2num(q,reshape(sprintf('%02X',data((29:32),:)),[8 MTiG.buffer])'); 
        my=hex2num(q,reshape(sprintf('%02X',data((33:36),:)),[8 MTiG.buffer])'); 
        mz=hex2num(q,reshape(sprintf('%02X',data((37:40),:)),[8 MTiG.buffer])');
        
        SILOP_DATA_BUFFER=[SILOP_DATA_BUFFER ax ay az rx ry rz mx my mz]; %#ok<AGROW>
        muestra=([256 1]*data(41:42,:))';
         
      case 1     % cal +cuat
        ax=hex2num(q,reshape(sprintf('%02X',data((5:8),:)),[8 MTiG.buffer])'); 
        ay=hex2num(q,reshape(sprintf('%02X',data((9:12),:)),[8 MTiG.buffer])'); 
        az=hex2num(q,reshape(sprintf('%02X',data((13:16),:)),[8 MTiG.buffer])'); 
        rx=hex2num(q,reshape(sprintf('%02X',data((17:20),:)),[8 MTiG.buffer])'); 
        ry=hex2num(q,reshape(sprintf('%02X',data((21:24),:)),[8 MTiG.buffer])'); 
        rz=hex2num(q,reshape(sprintf('%02X',data((25:28),:)),[8 MTiG.buffer])'); 
        mx=hex2num(q,reshape(sprintf('%02X',data((29:32),:)),[8 MTiG.buffer])'); 
        my=hex2num(q,reshape(sprintf('%02X',data((33:36),:)),[8 MTiG.buffer])'); 
        mz=hex2num(q,reshape(sprintf('%02X',data((37:40),:)),[8 MTiG.buffer])');
        
        qi=hex2num(q,reshape(sprintf('%02X',data((41:44),:)),[8 MTiG.buffer])'); 
        qii=hex2num(q,reshape(sprintf('%02X',data((45:48),:)),[8 MTiG.buffer])'); 
        qiii=hex2num(q,reshape(sprintf('%02X',data((49:52),:)),[8 MTiG.buffer])'); 
        qiv=hex2num(q,reshape(sprintf('%02X',data((53:56),:)),[8 MTiG.buffer])'); 
            
        SILOP_DATA_BUFFER=[SILOP_DATA_BUFFER ax ay az rx ry rz mx my mz qi qii qiii qiv]; %#ok<AGROW>
        muestra=([256 1]*data(57:58,:))';
       
      case 2     % cal +eul
        ax=hex2num(q,reshape(sprintf('%02X',data((5:8),:)),[8 MTiG.buffer])'); 
        ay=hex2num(q,reshape(sprintf('%02X',data((9:12),:)),[8 MTiG.buffer])'); 
        az=hex2num(q,reshape(sprintf('%02X',data((13:16),:)),[8 MTiG.buffer])'); 
        rx=hex2num(q,reshape(sprintf('%02X',data((17:20),:)),[8 MTiG.buffer])'); 
        ry=hex2num(q,reshape(sprintf('%02X',data((21:24),:)),[8 MTiG.buffer])'); 
        rz=hex2num(q,reshape(sprintf('%02X',data((25:28),:)),[8 MTiG.buffer])'); 
        mx=hex2num(q,reshape(sprintf('%02X',data((29:32),:)),[8 MTiG.buffer])'); 
        my=hex2num(q,reshape(sprintf('%02X',data((33:36),:)),[8 MTiG.buffer])'); 
        mz=hex2num(q,reshape(sprintf('%02X',data((37:40),:)),[8 MTiG.buffer])');
        
        roll=hex2num(q,reshape(sprintf('%02X',data((41:44),:)),[8 MTiG.buffer])'); 
        pitch=hex2num(q,reshape(sprintf('%02X',data((45:48),:)),[8 MTiG.buffer])'); 
        yaw=hex2num(q,reshape(sprintf('%02X',data((49:52),:)),[8 MTiG.buffer])'); 
  
        SILOP_DATA_BUFFER=[SILOP_DATA_BUFFER ax ay az rx ry rz mx my mz roll pitch yaw]; %#ok<AGROW>
        muestra=([256 1]*data(53:54,:))';
     
      case 3     % cal +mat
        ax=hex2num(q,reshape(sprintf('%02X',data((5:8),:)),[8 MTiG.buffer])'); 
        ay=hex2num(q,reshape(sprintf('%02X',data((9:12),:)),[8 MTiG.buffer])'); 
        az=hex2num(q,reshape(sprintf('%02X',data((13:16),:)),[8 MTiG.buffer])'); 
        rx=hex2num(q,reshape(sprintf('%02X',data((17:20),:)),[8 MTiG.buffer])'); 
        ry=hex2num(q,reshape(sprintf('%02X',data((21:24),:)),[8 MTiG.buffer])'); 
        rz=hex2num(q,reshape(sprintf('%02X',data((25:28),:)),[8 MTiG.buffer])'); 
        mx=hex2num(q,reshape(sprintf('%02X',data((29:32),:)),[8 MTiG.buffer])'); 
        my=hex2num(q,reshape(sprintf('%02X',data((33:36),:)),[8 MTiG.buffer])'); 
        mz=hex2num(q,reshape(sprintf('%02X',data((37:40),:)),[8 MTiG.buffer])');
        
        a=hex2num(q,reshape(sprintf('%02X',data((41:44),:)),[8 MTiG.buffer])'); 
        b=hex2num(q,reshape(sprintf('%02X',data((45:48),:)),[8 MTiG.buffer])'); 
        c=hex2num(q,reshape(sprintf('%02X',data((49:52),:)),[8 MTiG.buffer])'); 
        d=hex2num(q,reshape(sprintf('%02X',data((53:56),:)),[8 MTiG.buffer])'); 
        e=hex2num(q,reshape(sprintf('%02X',data((57:60),:)),[8 MTiG.buffer])'); 
        f=hex2num(q,reshape(sprintf('%02X',data((61:64),:)),[8 MTiG.buffer])'); 
        g=hex2num(q,reshape(sprintf('%02X',data((65:68),:)),[8 MTiG.buffer])'); 
        h=hex2num(q,reshape(sprintf('%02X',data((69:72),:)),[8 MTiG.buffer])');
        i=hex2num(q,reshape(sprintf('%02X',data((73:76),:)),[8 MTiG.buffer])'); 

        SILOP_DATA_BUFFER=[SILOP_DATA_BUFFER ax ay az rx ry rz mx my mz a b c d e f g h i]; %#ok<AGROW>
        muestra=([256 1]*data(77:78,:))';
  
      case 4      % LLA +Vel +Status
        lat=hex2num(q,reshape(sprintf('%02X',data((5:8),:)),[8 MTiG.buffer])'); 
        long=hex2num(q,reshape(sprintf('%02X',data((9:12),:)),[8 MTiG.buffer])'); 
        alt=hex2num(q,reshape(sprintf('%02X',data((13:16),:)),[8 MTiG.buffer])'); 
        vx=hex2num(q,reshape(sprintf('%02X',data((17:20),:)),[8 MTiG.buffer])'); 
        vy=hex2num(q,reshape(sprintf('%02X',data((21:24),:)),[8 MTiG.buffer])'); 
        vz=hex2num(q,reshape(sprintf('%02X',data((25:28),:)),[8 MTiG.buffer])'); 
        status=data(29,:)';
        
        SILOP_DATA_BUFFER=[SILOP_DATA_BUFFER lat long alt vx vy vz status]; %#ok<AGROW>
        muestra=([256 1]*data(30:31,:))';
        
     case 5      % cal + LLA+Vel+St
        ax=hex2num(q,reshape(sprintf('%02X',data((5:8),:)),[8 MTiG.buffer])'); 
        ay=hex2num(q,reshape(sprintf('%02X',data((9:12),:)),[8 MTiG.buffer])'); 
        az=hex2num(q,reshape(sprintf('%02X',data((13:16),:)),[8 MTiG.buffer])'); 
        rx=hex2num(q,reshape(sprintf('%02X',data((17:20),:)),[8 MTiG.buffer])'); 
        ry=hex2num(q,reshape(sprintf('%02X',data((21:24),:)),[8 MTiG.buffer])'); 
        rz=hex2num(q,reshape(sprintf('%02X',data((25:28),:)),[8 MTiG.buffer])'); 
        mx=hex2num(q,reshape(sprintf('%02X',data((29:32),:)),[8 MTiG.buffer])'); 
        my=hex2num(q,reshape(sprintf('%02X',data((33:36),:)),[8 MTiG.buffer])'); 
        mz=hex2num(q,reshape(sprintf('%02X',data((37:40),:)),[8 MTiG.buffer])');
        
        lat=hex2num(q,reshape(sprintf('%02X',data((41:44),:)),[8 MTiG.buffer])'); 
        long=hex2num(q,reshape(sprintf('%02X',data((45:48),:)),[8 MTiG.buffer])'); 
        alt=hex2num(q,reshape(sprintf('%02X',data((49:52),:)),[8 MTiG.buffer])'); 
        vx=hex2num(q,reshape(sprintf('%02X',data((53:56),:)),[8 MTiG.buffer])'); 
        vy=hex2num(q,reshape(sprintf('%02X',data((57:60),:)),[8 MTiG.buffer])'); 
        vz=hex2num(q,reshape(sprintf('%02X',data((61:64),:)),[8 MTiG.buffer])'); 
        status=data(65,:)';
        
        SILOP_DATA_BUFFER=[SILOP_DATA_BUFFER ax ay az rx ry rz mx my mz lat long alt vx vy vz status]; %#ok<AGROW>
        muestra=([256 1]*data(66:67,:))';        
        
    case 6      % RAW in+gps
        % Aún por realizar las transformaciones necesarias para que estos
        % datos sin calibrar (RAW), se puedan sacar del driver calibrados
        ax=hex2num(q,reshape(sprintf('%02X',data((5:6),:)),[4 MTiG.buffer])'); 
        ay=hex2num(q,reshape(sprintf('%02X',data((7:8),:)),[4 MTiG.buffer])'); 
        az=hex2num(q,reshape(sprintf('%02X',data((9:10),:)),[4 MTiG.buffer])'); 
        rx=hex2num(q,reshape(sprintf('%02X',data((11:12),:)),[4 MTiG.buffer])'); 
        ry=hex2num(q,reshape(sprintf('%02X',data((13:14),:)),[4 MTiG.buffer])'); 
        rz=hex2num(q,reshape(sprintf('%02X',data((15:16),:)),[4 MTiG.buffer])'); 
        mx=hex2num(q,reshape(sprintf('%02X',data((17:18),:)),[4 MTiG.buffer])'); 
        my=hex2num(q,reshape(sprintf('%02X',data((19:20),:)),[4 MTiG.buffer])'); 
        mz=hex2num(q,reshape(sprintf('%02X',data((21:22),:)),[4 MTiG.buffer])');
        temp=hex2num(q,reshape(sprintf('%02X',data((23:24),:)),[4 MTiG.buffer])');
        
        press=hex2num(q,reshape(sprintf('%02X',data((25:26),:)),[4 MTiG.buffer])');
        bprs=data((27:28),:)';
        itow=hex2num(q,reshape(sprintf('%02X',data((29:32),:)),[8 MTiG.buffer])'); % ojo i4 
        lat=hex2num(q,reshape(sprintf('%02X',data((33:36),:)),[8 MTiG.buffer])'); % ojo i4
        long=hex2num(q,reshape(sprintf('%02X',data((37:40),:)),[8 MTiG.buffer])'); 
        alt=hex2num(q,reshape(sprintf('%02X',data((41:44),:)),[8 MTiG.buffer])'); 
        vn=hex2num(q,reshape(sprintf('%02X',data((45:48),:)),[8 MTiG.buffer])'); 
        ve=hex2num(q,reshape(sprintf('%02X',data((48:51),:)),[8 MTiG.buffer])'); 
        vd=hex2num(q,reshape(sprintf('%02X',data((52:55),:)),[8 MTiG.buffer])'); 
        hacc=hex2num(q,reshape(sprintf('%02X',data((56:59),:)),[8 MTiG.buffer])'); 
        vacc=hex2num(q,reshape(sprintf('%02X',data((60:63),:)),[8 MTiG.buffer])'); 
        sacc=hex2num(q,reshape(sprintf('%02X',data((64:67),:)),[8 MTiG.buffer])'); 
        bgps=data(68,:)'; 

        SILOP_DATA_BUFFER=[SILOP_DATA_BUFFER ax ay az rx ry rz mx my mz temp press itow bprs lat long alt vn ve vd hacc vacc sacc bgps]; %#ok<AGROW>
        muestra=([256 1]*data(69:70,:))';
  end

  SILOP_DATA_BUFFER=[muestra SILOP_DATA_BUFFER];
  disp(['leidos ' num2str([muestra(1) muestra(end)])])
end

function MTiG=SetPeriod(MTiG,freq)
    % Envia el mensaje SetPeriod al objeto MTiG  ###
    % El proceso se queda bloqueado hasta recibir la informacion
    % Calcular la frecuencia de muestreo
    fm=[fix(115200/freq/256) mod(115200/freq,256)];
    % Cuerpo del mensaje (excepto el byte de checksum)
    msg=[250,255,4,2,fm];
    % Se calcula el cheksum y se coloca al final
    msg=[msg 256-mod(sum(msg(2:end)),256)];
    % Se envia por el puerto serie 
    if (MTiG.puerto.BytesAvailable>0)
        % Vaciar el puerto 
        disp(['>>> AVISO: Se descartaran ' int2str(MTiG.puerto.BytesAvailable) ' datos']);
        fread(MTiG.puerto,MTiG.puerto.BytesAvailable,'uint8');
    end
    % El valor del TimeOut se fija a 1 segundo
    MTiG.puerto.timeOut=1;
    fwrite(MTiG.puerto,msg,'uint8','async');
    % Se espera a recibir la contestacion
    [ack,cnt,msg]=fread(MTiG.puerto,5,'uint8');
    if (~isempty(msg))
        disp(msg);
        error('no se ha recibido respuesta al comando setperiod');
    else
        if (mod(sum(ack(2:end)),256)~=0)
            error('Error de checksum durante el comando setperiod');
        else
            if (ack(3)~=5)
                error('Error en la secuencia de mensajes durante el comando setperiod');
            end
        end
    end
    
end

function MTiG=SetMTOutputMode(MTiG, orientformat)
   switch (orientformat)
       case 0
           outmode=[0 2];          % datos calibrados
           outsett=[0 7 192 1];      
       case 1         
           outmode=[0 6];          % datos calibrados y orientados
           outsett=[0 0 0 1];      %  (cuaternas)
       case 2
           outmode=[0 6];          % datos calibrados y orientados
           outsett=[0 0 0 5];      %  (ang d Euler)
       case 3
           outmode=[0 6];          % datos calibrados y orientados
           outsett=[0 0 0 9];      %  (matrix)
            
       case 4                      % Posición+Vel+Status /B/                                 
           outmode=[8 48];         % 4,5,11 a 1
           outsett=[0 0 0 1];         
       case 5                      % Calibrado+ (Posición+Vel+Status)                                       
           outmode=[8 50];
           outsett=[0 0 0 1];
       case 6                      % El RAW = RAW Inertial + RAW GPS  
           outmode=[80 0];
           outsett=[0 0 0 1];                                
   end
   
   % Enviar el mensaje SetOutputMode ###
   % Cuerpo del mensaje (excepto el byte de checksum)
   msg=[250,255,208,2,outmode];
   % Se calcula el cheksum y se coloca al final
   msg=[msg 256-mod(sum(msg(2:end)),256)]; %#ok<AGROW>
   % Se envia por el puerto serie 
   if (MTiG.puerto.BytesAvailable>0)
       % Vaciar el puerto 
       disp(['>>> AVISO: Se descartaran ' int2str(MTiG.puerto.BytesAvailable) ' datos']);
       fread(MTiG.puerto,MTiG.puerto.BytesAvailable,'uint8');
   end
   % El valor del TimeOut se fija a 1 segundo
   MTiG.puerto.Timeout=1;
   fwrite(MTiG.puerto,msg,'uint8','async');
   % Se espera a recibir la contestacion
   [ack,cnt,msg]=fread(MTiG.puerto,5,'uint8');
   if (~isempty(msg))
       error('no se ha recibido respuesta al comando setmtoutputmode');
   else
       if (mod(sum(ack(2:end)),256)~=0)
           error('Error de checksum durante el comando setmtoutputmode');
       else
           if (ack(3)~=209)
               error('Error en la secuencia de mensajes durante el comando setmtoutputmode');
           end
       end
   end

   % Enviar el mensaje SetOutputSettings ###
   % Cuerpo del mensaje (excepto el byte de checksum)
   msg=[250,255,210,4,outsett];
   % Se calcula el cheksum y se coloca al final
   msg=[msg 256-mod(sum(msg(2:end)),256)]; %#ok<AGROW>
   % Se envia por el puerto serie 
   if (MTiG.puerto.BytesAvailable>0)
       % Vaciar el puerto 
       disp(['>>> AVISO: Se descartaran ' int2str(MTiG.puerto.BytesAvailable) ' datos']);
       fread(MTiG.puerto,MTiG.puerto.BytesAvailable,'uint8');
   end
   % El valor del TimeOut se fija a 1 segundo
   MTiG.puerto.Timeout=1;
   fwrite(MTiG.puerto,msg,'uint8','async');
   % Se espera a recibir la contestacion
   [ack,cnt,msg]=fread(MTiG.puerto,5,'uint8');
   if (~isempty(msg))
       disp(msg);
       error('no se ha recibido respuesta durante el comando setmtoutputmode');
   else
       if (mod(sum(ack(2:end)),256)~=0)
           error('Error de checksum durante el comando setmtoutputmode');
       else
           if (ack(3)~=211)
               error('Error en la secuencia de mensajes durante el comando setmtoutputmode');
           end
       end
   end
   
end
