% SETOBJECTALIGNMENT Envía el mensaje SetObjectAlignment al objeto XBusMaster
%
% SETOBJECTALIGNMENT Envía el mensaje SetObjectAlignment al objeto XBusMaster. El proceso
%         se queda bloqueado hasta recibir la respuesta
% 
% Syntax: XBusMaster=SetObjectAlignment(XBusMaster,k,matriz)
% 
% Input parameters:
%   XBusMaster-> Objeto con la información del dispositivo.
%   k        -> Número de dispositivo al que aplicar el cambio. 
%   matriz -> Matriz de rotación a aplicar con respecto a los ejes originales del dispositivo
%
% Output parameters:
%   XBusMaster- Es el mismo objeto de entrada que puede haber sido
%               modificado durante la llamada.
%
% Examples:
%
% See also: 

% Author:   Rafael C. Gonzalez de los Reyes
% History:  


function XBusMaster=SetObjectAlignment(XBusMaster,k,matriz)

% Envia el mensaje ResetOrientation a todos los dispositivos conectados
% error vale 1 si no se recibe el mensaje de ack
% El proceso se queda bloqueado hasta recibir el ack
matriz=cast(matriz,'single');
matriz=matriz';

%for k=1:XBusMaster.Conf.DevNum   %Esto aplica el cambio a todos los dispositivos
    % Cuerpo del mensaje (excepto el byte de checksum)
    msg=[250,k,224,9*4, (typecast(swapbytes(matriz(:)),'uint8'))'];
    % Se calcula el cheksum y se coloca al final
    msg=[msg 256-mod(sum(msg(2:end)),256)];
    % Se envia por el puerto serie 
    while (XBusMaster.puerto.BytesAvailable>0)
        % Vaciar el puerto 
        % OJO!!! Los datos se perderan
        disp(['>>> AVISO: Se descartaran ' int2str(XBusMaster.puerto.BytesAvailable) ' datos']);
        fread(XBusMaster.puerto,XBusMaster.puerto.BytesAvailable,'uint8');
    end
    % El valor del TimeOut se fija a 1 segundo
    %tout=XBusMaster.puerto.TimeOut;
    XBusMaster.puerto.Timeout=1;
    fwrite(XBusMaster.puerto,msg,'uint8','async');  
    % Se espera a recibir la contestacion
    % Se supone que el buffer de entrada esta vacio
    %msg=[];
    [ack,cnt,msg]=fread(XBusMaster.puerto,5,'uint8');
    if (~isempty(msg))
        disp(msg);
        error('no se ha recibido respuesta al comando setobjectalignement');
    else
        if (mod(sum(ack(2:end)),256)~=0)
        error('Error de checksum durante el comando setobjectalignment');
        else
            if (ack(3)~=225)
                error('Error en la secuencia de mensajes durante el comando setobjectalignment');
            end
        end
    end
%end
