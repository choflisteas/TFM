%ALG_EST_2D Algoritmo para la estimacion de la posicion en 2d
%
%ALG_EST_2D Algoritmo para la estimacion de la posicion en 2d. 
%Se puede configurar mediante:
%    addalgoritmo('alg_est_2d', {'P.X','P.Y'}, {'P.Dist','P.Orient'}, []);
%
%Parametros: como todos los alg_*. resultados anteriores, se�ales a usar(distancia recorrida en cada paso y orientacion),
% y parametros(vacio en este caso).

%Creado: 01-02-2008 por Diego

function [resultadox, resultadoy] = alg_est_2d(previos, senhales, params)  %#ok<INUSD>

    distancias = senhales(:,1);
    angulos = senhales(:,2);
	
    resultadox=previos(:,1);
    resultadoy=previos(:,2);
        x=0;y=0;
        	
        pasos=find(~isnan(distancias));
	pasos=pasos';
	if (~isempty(pasos))
		for k=pasos(1:end)
            if (isnan(resultadox(k))) 
                x=x+distancias(k)*cos(angulos(k));
                y=y+distancias(k)*sin(angulos(k));
                resultadox(k)=x;
                resultadoy(k)=y;
            else  %ya estaba calculado
				x=resultadox(k);
				y=resultadoy(k);
            end
		end
	end

        

