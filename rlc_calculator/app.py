from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            calc_type = request.form['calc_type']
            resistance = float(request.form['resistance'])
            frequency = float(request.form['frequency'])
            voltage = float(request.form['voltage'])
            
            V = voltage  # User-supplied voltage

            if calc_type == 'RLC':
                capacitance = float(request.form['capacitance']) * 1e-6  # Convert from microfarads to farads
                inductance = float(request.form['inductance']) * 1e-3    # Convert from millihenrys to henrys
                Xc = 1 / (2 * np.pi * frequency * capacitance)
                Xl = 2 * np.pi * frequency * inductance
            elif calc_type == 'RC':
                capacitance = float(request.form['capacitance']) * 1e-6  # Convert from microfarads to farads
                Xc = 1 / (2 * np.pi * frequency * capacitance)
                Xl = 0
            elif calc_type == 'RL':
                inductance = float(request.form['inductance']) * 1e-3  # Convert from millihenrys to henrys
                Xc = 0
                Xl = 2 * np.pi * frequency * inductance

            # Calculate impedance
            Z = complex(resistance, Xl - Xc)
            magnitude = abs(Z)  # This is the impedance
            power_factor = resistance / magnitude
            phase = np.degrees(np.arccos(power_factor))

            I = V / magnitude
            P_active = V * I * power_factor
            Q_reactive = V * I * np.sin(np.radians(phase))
            S_apparent = V * I

            # Power through components
            P_resistor = I**2 * resistance
            P_capacitor = -(I**2 * Xc) if Xc else 0
            P_inductor = I**2 * Xl if Xl else 0

            # Create the phasor diagram
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.quiver(0, 0, resistance, 0, angles='xy', scale_units='xy', scale=1, color='r', label='VR = IR')
            if (Xl != 0):
                ax.quiver(0, 0, 0, Xl, angles='xy', scale_units='xy', scale=1, color='b', label='VL')
            if (Xc != 0):
                ax.quiver(0, 0, 0, -Xc, angles='xy', scale_units='xy', scale=1, color='g', label='VC')
            ax.quiver(0, 0, resistance, (Xl - Xc), angles='xy', scale_units='xy', scale=1, color='k', label='V = IZ')

            # Annotate magnitudes on the graph
            ax.text(resistance, 1.5, f'VR = {resistance:.2f} Ω', fontsize=15, color='r', ha='center', va='center')
            if (Xl != 0):
                ax.text(1.5, Xl+3, f'VL = {Xl:.2f} Ω', fontsize=15, color='b', ha='center', va='center')
            if (Xc != 0):
                ax.text(1.5, -Xc-3, f'VC = {Xc:.2f} Ω', fontsize=15, color='g', ha='center', va='center')
                ax.text(resistance, Xl - Xc, f'Z = {magnitude:.2f} Ω', fontsize=15, color='k', ha='center', va='center')
                ax.annotate(r"$\phi$" + f" = {phase:.2f}°", xy=(resistance * 0.8, (Xl - Xc) * 0.5), fontsize=15, color='black')
                ax.plot([resistance, resistance], [0, Xl - Xc], 'k--')

                # Draw the axes
                ax.axhline(0, color='black', linewidth=0.5)
                ax.axvline(0, color='black', linewidth=0.5)
                max_y_val = max(abs(Xl), abs(-Xc))
                buffer = 10
                ax.set_ylim(-max_y_val - buffer, max_y_val + buffer)

                # Ensure the x-axis extends enough to display the resistance
                ax.set_xlim(-buffer, resistance + buffer)

                ax.set_xlabel('Real (Ω)', fontsize=15)
                ax.set_ylabel('Imaginary (Ω)', fontsize=15)
                ax.legend(fontsize=12)
                ax.set_title('Phasor Diagram', fontsize=18)

                # Save the plot to a bytes object
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_url = base64.b64encode(buf.getvalue()).decode('utf8')

                data = {
                    'impedance': magnitude,
                    'phase': phase,
                    'power_factor': power_factor,
                    'reactive_power': Q_reactive,
                    'active_power': P_active,
                    'apparent_power': S_apparent,
                    'plot_url': plot_url,
                    'current': I,
                    'power_resistor': P_resistor,
                    'power_capacitor': P_capacitor,
                    'power_inductor': P_inductor
                }

                return jsonify(data)

        except ValueError:
            return jsonify({'error': 'Invalid input. Please enter numeric values.'})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
