% build_AlIon_SiC_SimulinkModel.m
% Programmatically create a Simulink model for AeroForge framework
% Computes electric aircraft range using Al-ion + SiC system parameters

model = 'AeroForge_AlIon_SiC_System';
if bdIsLoaded(model)
    close_system(model, 0);
end
new_system(model);
open_system(model);

% Block positions for clean layout
x0 = 30; y0 = 30; dx = 140; dy = 60;

% Add constant blocks for all AeroForge parameters
inputs = {'eta_system','Epack_wh_per_kg','m_batt_kg','m_total_kg','g',...
         'L_over_D','SFC_eq','harvest_kW','sic_efficiency_gain'};

for i = 1:numel(inputs)
    blk = add_block('simulink/Sources/Constant', [model '/' inputs{i}],...
        'Position',[x0, y0 + (i-1)*dy, x0+50, y0+30 + (i-1)*dy],...
        'Value','0');
end

% Set AeroForge default values based on our Al-ion + SiC analysis
set_param([model '/eta_system'],'Value','0.92');              % enhanced with SiC
set_param([model '/Epack_wh_per_kg'],'Value','450');          % Al-ion target
set_param([model '/m_batt_kg'],'Value','25000');              % 25-ton pack
set_param([model '/m_total_kg'],'Value','80000');             % total aircraft
set_param([model '/g'],'Value','9.80665');
set_param([model '/L_over_D'],'Value','22');                  % optimized aero
set_param([model '/SFC_eq'],'Value','0.00015');               % calibrated
set_param([model '/harvest_kW'],'Value','15');                % multi-modal harvest
set_param([model '/sic_efficiency_gain'],'Value','1.08');     % 8% SiC boost

% Create input vector aggregator
packedValue = sprintf('[%s %s %s %s %s %s %s %s %s]', inputs{:});
aggBlock = add_block('simulink/Sources/Constant', [model '/AeroForge_inputs'], ...
    'Position',[x0+4*dx, y0+4*dy, x0+4*dx+120, y0+4*dy+30],...
    'Value',packedValue);

% Add AeroForge range calculator (Interpreted MATLAB Function)
rangeBlock = add_block('simulink/User-Defined Functions/Interpreted MATLAB Function', ...
    [model '/AeroForge_RangeCalc'],...
    'Position',[x0+6*dx, y0+4*dy, x0+6*dx+200, y0+4*dy+100],...
    'FunctionName','AeroForge_RangeCalc');

% Connect input to range calculator
add_line(model, 'AeroForge_inputs/1', 'AeroForge_RangeCalc/1', 'autorouting','on');

% Add output displays
add_block('simulink/Sinks/Display', [model '/Range_km_Display'],...
    'Position',[x0+8*dx, y0+3*dy, x0+8*dx+100, y0+3*dy+30]);
add_block('simulink/Sinks/Display', [model '/Energy_Efficiency_Display'],...
    'Position',[x0+8*dx, y0+5*dy, x0+8*dx+100, y0+5*dy+30]);

% Connect outputs
add_line(model, 'AeroForge_RangeCalc/1', 'Range_km_Display/1', 'autorouting','on');

% Save the AeroForge model
save_system(model);
open_system(model);

disp('AeroForge Simulink model created: AeroForge_AlIon_SiC_System.slx');
disp('Make sure AeroForge_RangeCalc.m is on the MATLAB path.');
disp('Model ready for Al-ion + SiC range analysis!');
