%ALG_PLOT_POS2D Algoritmo para la representacion de la posicion en 2d
%
%ALG_PLOT_SENHALES Algoritmo para la representacion de la posicion en 2d
%Se puede configurar mediante:
%    addalgoritmo('alg_plot_pos2d', 1, {'Punto.X','Punto.Y'}, []);
%
%Parámetros: como todos los alg_*. resultados anteriores, señales a usar{coordenadas x e y estimadas} 
% parametros(vacio en este caso) y dependencias.
% El dato devuelto es para consumo propio (no redibujar puntos ya
% dibujados)

%Creado: 06-02-2008 por Diego

function yadibujado=alg_plot_pos2d(resultados, senhales, params) %#ok<INUSD,INUSL>



	persistent mifigura
    persistent midata
    if (isempty(mifigura))
    		mifigura=figure;
            midata=[0,0];
    end
    
    figure(mifigura);
    ultimodibujado=find(~isnan(resultados),1,'last');
    if (isempty(ultimodibujado))
        ultimodibujado=1;
    end
    indices=find(~isnan(senhales(ultimodibujado+1:end,1)))+ultimodibujado;
    yadibujado=resultados;
    if (~isempty(indices))
        yadibujado(1:max(indices))=1;
        midata=[midata;senhales(indices,1), senhales(indices,2)];
        plot(midata(:,1),midata(:,2));
        drawnow;
    end








% Old working code
%function alg_plot_pos2d(valores_actuales, senhales, params, dependencias) %#ok<INUSL>
%     persistent mifigura
% 	if (isempty(mifigura))
%     		mifigura=figure;
% 	end
% 
% 
%     figure(mifigura);    
%     
%     indices=find(~isnan(dependencias(:,1)));
%     plot(dependencias(indices,1), dependencias(indices,2));
%     drawnow;

