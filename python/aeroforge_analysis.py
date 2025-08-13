#!/usr/bin/env python3
"""
AeroForge Python Monte-Carlo Analysis
Al-ion + SiC Electric Aircraft Range Simulation
Implements the theoretical framework with uncertainty quantification
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set styling for professional plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def aeroforge_range_calc(eta_system, epack_wh_per_kg, m_batt_kg, m_total_kg, 
                        g, l_over_d, sfc_eq, harvest_kw, sic_efficiency_gain, 
                        cruise_hours=6):
    """
    AeroForge range calculation - Python implementation
    
    Returns range in km for Al-ion + SiC electric aircraft system
    """
    # Battery energy
    e_pack_total_wh = epack_wh_per_kg * m_batt_kg
    
    # Harvesting energy
    e_harvest_wh = harvest_kw * 1000 * cruise_hours
    
    # SiC-enhanced efficiency
    eta_effective = eta_system * sic_efficiency_gain
    
    # Total usable energy
    e_usable_wh = eta_effective * (e_pack_total_wh + e_harvest_wh)
    
    # Electric Breguet calculation
    r_m = e_usable_wh / (g * l_over_d * sfc_eq * m_total_kg)
    r_km = np.maximum(0, np.minimum(50000, r_m / 1000.0))  # Bounded
    
    return r_km

def run_aeroforge_montecarlo(n_runs=2000, seed=42):
    """
    Execute AeroForge Monte-Carlo sensitivity analysis
    """
    np.random.seed(seed)
    print("=== AeroForge Python Monte-Carlo Analysis ===")
    print(f"Runs: {n_runs}")
    
    # Nominal parameters (Al-ion + SiC system)
    params_nom = {
        'eta_system': 0.92,        # SiC-enhanced efficiency
        'epack_wh_per_kg': 450.0,  # Al-ion target density
        'm_batt_kg': 25000.0,      # Battery pack mass
        'm_total_kg': 80000.0,     # Total aircraft mass
        'g': 9.80665,              # Gravity
        'l_over_d': 22.0,          # Aerodynamic efficiency
        'sfc_eq': 0.00015,         # Equivalent specific consumption
        'harvest_kw': 15.0,        # Multi-modal harvesting
        'sic_efficiency_gain': 1.08 # SiC boost factor
    }
    
    # Generate parameter distributions with engineering uncertainties
    samples = {}
    
    # Battery density: ±25% (major Al-ion uncertainty)
    samples['epack'] = np.maximum(200, 
        params_nom['epack_wh_per_kg'] * (1 + 0.25 * np.random.randn(n_runs)))
    
    # Aerodynamics: ±15%
    samples['l_over_d'] = np.maximum(15, 
        params_nom['l_over_d'] * (1 + 0.15 * np.random.randn(n_runs)))
    
    # Harvesting: ±40% (weather dependent)
    samples['harvest'] = np.maximum(0, 
        params_nom['harvest_kw'] * (1 + 0.4 * np.random.randn(n_runs)))
    
    # SiC gain: ±20% (integration challenges)
    samples['sic_gain'] = np.maximum(1.0, 
        params_nom['sic_efficiency_gain'] * (1 + 0.2 * np.random.randn(n_runs)))
    
    # System efficiency: ±10%
    samples['eta'] = np.clip(
        params_nom['eta_system'] * (1 + 0.1 * np.random.randn(n_runs)),
        0.7, 0.98)
    
    # Calculate ranges for all samples
    ranges_km = np.zeros(n_runs)
    
    for i in range(n_runs):
        ranges_km[i] = aeroforge_range_calc(
            samples['eta'][i], samples['epack'][i], params_nom['m_batt_kg'],
            params_nom['m_total_kg'], params_nom['g'], samples['l_over_d'][i],
            params_nom['sfc_eq'], samples['harvest'][i], samples['sic_gain'][i]
        )
    
    return samples, ranges_km, params_nom

def analyze_results(samples, ranges_km):
    """
    Statistical analysis and reporting
    """
    # Basic statistics
    mu = np.mean(ranges_km)
    sigma = np.std(ranges_km) 
    median_range = np.median(ranges_km)
    p5, p95 = np.percentile(ranges_km, [5, 95])
    
    # Target achievement rates
    target_5k = np.sum(ranges_km >= 5000) / len(ranges_km) * 100
    target_10k = np.sum(ranges_km >= 10000) / len(ranges_km) * 100
    
    print(f"\n=== AeroForge Results Summary ===")
    print(f"Range Statistics:")
    print(f"  Mean: {mu:.0f} km (±{sigma:.0f} km std)")
    print(f"  Median: {median_range:.0f} km")
    print(f"  90% Confidence: {p5:.0f} - {p95:.0f} km")
    print(f"\nTarget Achievement:")
    print(f"  ≥5,000 km: {target_5k:.1f}% of cases")
    print(f"  ≥10,000 km: {target_10k:.1f}% of cases")
    
    # Correlation analysis
    correlations = {}
    for param in ['epack', 'l_over_d', 'harvest', 'sic_gain', 'eta']:
        correlations[param] = np.corrcoef(samples[param], ranges_km)[0,1]
    
    print(f"\nParameter Correlations with Range:")
    for param, corr in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
        print(f"  {param}: {corr:.3f}")
    
    return {
        'mean': mu, 'std': sigma, 'median': median_range,
        'p5': p5, 'p95': p95, 'target_5k': target_5k, 'target_10k': target_10k,
        'correlations': correlations
    }

def create_visualizations(samples, ranges_km, stats, save_plots=True):
    """
    Generate comprehensive analysis plots
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Main range distribution
    plt.subplot(3, 3, 1)
    plt.hist(ranges_km, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(5000, color='red', linestyle='--', linewidth=2, label='5,000 km target')
    plt.axvline(10000, color='green', linestyle='--', linewidth=2, label='10,000 km target')
    plt.axvline(stats['mean'], color='orange', linestyle='-', linewidth=2, label=f'Mean: {stats["mean"]:.0f} km')
    plt.xlabel('Range (km)')
    plt.ylabel('Frequency')
    plt.title(f'AeroForge Range Distribution\n(μ={stats["mean"]:.0f}, σ={stats["std"]:.0f})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Sensitivity scatter plots
    plot_configs = [
        ('epack', 'Battery Energy Density (Wh/kg)', 2),
        ('l_over_d', 'Lift-to-Drag Ratio', 3),
        ('harvest', 'Harvesting Power (kW)', 4),
        ('sic_gain', 'SiC Efficiency Gain', 5),
        ('eta', 'System Efficiency', 6)
    ]
    
    for param, xlabel, subplot_idx in plot_configs:
        plt.subplot(3, 3, subplot_idx)
        plt.scatter(samples[param], ranges_km, alpha=0.5, s=20)
        plt.xlabel(xlabel)
        plt.ylabel('Range (km)')
        plt.title(f'Range vs {xlabel.split(" ")[0]}\n(r={stats["correlations"][param]:.3f})')
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(samples[param], ranges_km, 1)
        p = np.poly1d(z)
        plt.plot(samples[param], p(samples[param]), "r--", alpha=0.8)
    
    # Box plot of ranges by parameter quartiles
    plt.subplot(3, 3, 7)
    epack_quartiles = pd.qcut(samples['epack'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
    df_box = pd.DataFrame({'Range': ranges_km, 'Battery_Quartile': epack_quartiles})
    sns.boxplot(data=df_box, x='Battery_Quartile', y='Range')
    plt.title('Range by Battery Density Quartile')
    plt.ylabel('Range (km)')
    
    # Cumulative distribution
    plt.subplot(3, 3, 8)
    sorted_ranges = np.sort(ranges_km)
    cumulative = np.arange(1, len(sorted_ranges) + 1) / len(sorted_ranges)
    plt.plot(sorted_ranges, cumulative * 100, linewidth=2)
    plt.axvline(5000, color='red', linestyle='--', alpha=0.7, label='5,000 km')
    plt.axvline(10000, color='green', linestyle='--', alpha=0.7, label='10,000 km')
    plt.xlabel('Range (km)')
    plt.ylabel('Cumulative Probability (%)')
    plt.title('Range Cumulative Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Parameter importance (correlation magnitude)
    plt.subplot(3, 3, 9)
    param_names = list(stats['correlations'].keys())
    param_corrs = [abs(stats['correlations'][p]) for p in param_names]
    param_labels = ['Battery Density', 'Aerodynamics', 'Harvesting', 'SiC Gain', 'Efficiency']
    
    bars = plt.bar(param_labels, param_corrs, color=['red', 'blue', 'green', 'orange', 'purple'])
    plt.ylabel('|Correlation| with Range')
    plt.title('Parameter Sensitivity Ranking')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Add correlation values on bars
    for bar, corr in zip(bars, param_corrs):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{corr:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('AeroForge_Python_Analysis.png', dpi=300, bbox_inches='tight')
        print(f"\nPlots saved to: AeroForge_Python_Analysis.png")
    
    plt.show()

def main():
    """
    Main execution function
    """
    # Run Monte-Carlo analysis
    samples, ranges_km, params_nom = run_aeroforge_montecarlo(n_runs=2000)
    
    # Analyze results
    stats = analyze_results(samples, ranges_km)
    
    # Create comprehensive dataset
    results_df = pd.DataFrame({
        'run': range(1, len(ranges_km) + 1),
        'eta_system': samples['eta'],
        'epack_wh_per_kg': samples['epack'],
        'l_over_d': samples['l_over_d'],
        'harvest_kw': samples['harvest'],
        'sic_efficiency_gain': samples['sic_gain'],
        'range_km': ranges_km
    })
    
    # Save results
    results_df.to_csv('AeroForge_Python_Results.csv', index=False)
    print(f"\nDetailed results saved to: AeroForge_Python_Results.csv")
    
    # Create visualizations
    create_visualizations(samples, ranges_km, stats)
    
    return results_df, stats

if __name__ == "__main__":
    # Execute AeroForge analysis
    results_df, statistics = main()
    
    print("\n=== AeroForge Analysis Complete ===")
    print("Ready for publication and further development!")
