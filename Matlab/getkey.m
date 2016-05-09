function ch = getkey(clear) 

% GETKEY - get a single keypress
%   CH = GETKEY waits for a keypress and returns the ASCII code. Accepts
%   all ascii characters, including backspace (8), space (32), enter (13),
%   etc, that can be typed on the keyboard. Non-ascii keys (ctrl, alt, ..)
%   return a NaN. CH is a double. 
%   Si recibe un parámetro destruye la ventana que tiene.
%
%   This function is kind of a workaround for getch in C. It uses a modal, but
%   non-visible window, which does show up in the taskbar.
%   C-language keywords: KBHIT, KEYPRESS, GETKEY, GETCH
%
%   Examples:

% for Matlab 6.5
% version 1.1 (dec 2006)
% author : Jos van der Geest
% email  : jos@jasen.nl
%
% History
% 2005 - creation
% dec 2006 - modified lay-out and help
% 13-02-2008- modificada para esperar un tiempo máximo y no bloquear el proceso.    
% modificada para no perder tiempo creando y destruyendo figuras dentro del
% bucle principal de playsilop()

% Determine the callback string to use
persistent fh

if nargin > 0
    delete(fh)
    return
end

callstr = ['set(gcbf,''Userdata'',double(get(gcbf,''Currentcharacter''))) ; uiresume '] ; %#ok<NBRAK>

% Set up the figure
% May be the position property  should be individually tweaked to avoid visibility
if (isempty(fh))
    fh = figure('keypressfcn',callstr, ...
        'windowstyle','modal',...    
        'position',[0 0 1 1],...
        'Name','GETKEY', ...
        'userdata','timeout') ;
end
try
    % Wait for something to happen
    uiwait(fh,1);
    ch = get(fh,'Userdata') ;
    if isempty(ch),
        ch = NaN ; 
    end
catch
    % Something went wrong, return and empty matrix.
    ch = [] ;
end

%delete(fh) ;
