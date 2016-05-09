% REQOBJECTALIGNMENT Envía el mensaje ReqObjectAlignment al objeto XBusMaster
%
% REQOBJECTALIGNMENT Envía el mensaje ReqObjectAlignment al objeto XBusMaster. El proceso
%         se queda bloqueado hasta recibir la respuesta
% 
% Syntax: XBusMaster=ReqObjectAlignment(XBusMaster,matriz)
% 
% Input parameters:
%   XBusMaster-> Objeto con la información del dispositivo.
%   p -> Identificador del sensor, tal y como se proporciona en id_disp
%
% Output parameters:
%   XBusMaster- Es el mismo objeto de entrada que puede haber sido
%               modificado durante la llamada.
%               La información de las orientaciones queda en XBusMaster.Conf.Dev(k).Orientacion
%
% Examples:
%
% See also: 

% Author:   Rafael C. Gonzalez de los Reyes
% History:  

function XBusMaster=ReqObjectAlignment(XBusMaster,p)

% Envia el mensaje ResetOrientation a todos los dispositivos conectados
% error vale 1 si no se recibe el mensaje de ack
% El proceso se queda bloqueado hasta recibir el ack

k=p;
%for k=1:XBusMaster.Conf.DevNum
    % Cuerpo del mensaje (excepto el byte de checksum)
    msg=[250,k,224,0];
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
    [ack,cnt,msg]=fread(XBusMaster.puerto,5+9*4,'uint8');
    error=0;
    if (~isempty(msg))
        disp(msg);
        error('no se ha recibido respuesta al comando reqobjectalignment');
    else
        if (mod(sum(ack(2:end)),256)~=0)
        error('Error de checksum durante el comando reqobjectalignment');
        else
            if (ack(3)~=225)
                error('Error en la secuencia de mensajes durante el comando reqobjectaligment');
            end
        end
    end
    q=quantizer('Mode','single');
    XBusMaster.Conf.Dev(k).Orientacion=reshape(hex2num(q,reshape(sprintf('%02X',ack(5:end-1)),[8 9])'),[3 3])';
%end
