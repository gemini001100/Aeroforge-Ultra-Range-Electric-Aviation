function R_km = AeroForge_RangeCalc(input_vec)
% AeroForge_RangeCalc - Electric range calculation for Al-ion + SiC system
% Implements the theoretical framework from our AeroForge design
%
% Input vector: [eta_system, Epack_wh_per_kg, m_batt_kg, m_total_kg, g, 
%                L_over_D, SFC_eq, harvest_kW, sic_efficiency_gain]
%
% Returns: R_km - Range in kilometers

% Unpack AeroForge parameters
eta_system           = double(input_vec(1));  % Base system efficiency
Epack_wh_per_kg     = double(input_vec(2));  % Al-ion pack density
m_batt_kg           = double(input_vec(3));  % Battery mass
m_total_kg          = double(input_vec(4));  % Total aircraft mass
g                   = double(input_vec(5));  % Gravity
L_over_D            = double(input_vec(6));  % Lift-to-drag ratio
SFC_eq              = double(input_vec(7));  % Equivalent specific consumption
harvest_kW          = double(input_vec(8));  % Harvesting power
sic_efficiency_gain = double(input_vec(9));  % SiC enhancement factor

% AeroForge Energy Calculations
% Step 1: Base Al-ion battery energy
E_pack_total_Wh = Epack_wh_per_kg * m_batt_kg;

% Step 2: Harvesting contribution (6-hour cruise assumption)
cruise_hours = 6;
E_harvest_Wh = harvest_kW * 1000 * cruise_hours;

% Step 3: SiC efficiency enhancement
eta_effective = eta_system * sic_efficiency_gain;

% Step 4: Total usable energy with all AeroForge enhancements
E_usable_Wh = eta_effective * (E_pack_total_Wh + E_harvest_Wh);

% Step 5: Electric Breguet range calculation
% Adapted for electric propulsion: R = E_usable / (Weight × Drag × SFC_eq)
R_m = E_usable_Wh / (g * L_over_D * SFC_eq * m_total_kg);
R_km = R_m / 1000;

% AeroForge safety bounds - clip non-physical results
if ~isfinite(R_km) || R_km < 0
    R_km = 0;
elseif R_km > 50000  % Sanity check - no aircraft flies 50,000 km!
    R_km = 50000;
end

% Add some AeroForge diagnostics (optional)
if nargout > 1
    % Could return additional metrics like energy breakdown, efficiency, etc.
    diagnostics.pack_energy_Wh = E_pack_total_Wh;
    diagnostics.harvest_energy_Wh = E_harvest_Wh;
    diagnostics.effective_efficiency = eta_effective;
    diagnostics.total_usable_Wh = E_usable_Wh;
end

end
