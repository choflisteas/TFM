%% SILOPDEMO Demostración de las capacidades de la toolbox
% SILOPDEMO Muestra la forma de usar la toolbox para el desarrollo rápido de aplicaciones mediante 
% un ejemplo de uso
%


%% Se crea la configuración inicial para la ejecución de la aplicación
% llamando a initsilop()
initsilop(); 


%% Se añaden los IMUS con los que se trabajará
% En este caso un IMU en el COG
addimu('COG', 204);


%% Nos conectamos al sistema de adquisición de datos.
% En este caso escogemos hacerlo trabajando en simulación y con un fichero
% de log
connectsilop('Temporizador','test.log'); %Conectamos al sistema de muestreo


%% Añadimos los algoritmos necesarios.
% Añadimos el algoritmo de deteccion de eventos, para localizar los instantes de HS y TO
addalgoritmo('alg_det_event', {'COG.HS','COG.TO'}, {'COG.Acc_Z', 'COG.Acc_X'}, []);

%% Añadimos los algoritmos restantes,
% medicion de pasos, estimacion de la orientacion, calculo de posiciones 2d
% y representación de la posición en 2d
addalgoritmo('alg_est_dist_pendulo' , {'COG.Dist'}, {'COG.Acc_Z','COG.HS'}, []);
addalgoritmo('alg_est_orient_gyro', {'COG.Orient'}, {'COG.G_Z'}, []);
addalgoritmo('alg_est_2d', {'COG.X','COG.Y'}, {'COG.Dist','COG.Orient'}, []);
addalgoritmo('alg_plot_pos2d', 1, {'COG.X','COG.Y'}, []);
    
%% Se pone en marcha el proceso
% Se detiene mediante la pulsación de la tecla ESC
playsilop();
