import numpy as np
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO

app = Flask(__name__)

def plot_monoprotic(concentration, pka, ph_range):
    ka = 10**-pka
    concentration_H = 10**-ph_range
    concentration_OH = 10**-(14-ph_range)
    logH = np.log10(concentration_H)
    logOH = np.log10(concentration_OH)
    alpha0 = 1/((ka/concentration_H)+1)
    alpha1 = 1/(1+(concentration_H/ka))
    logC_alpha0 = np.log10(alpha0*concentration)
    logC_alpha1 = np.log10(alpha1*concentration)
    buffer = 2.303 * concentration * alpha0 * alpha1

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.plot(ph_range, alpha0, label = 'Alpha 0')
    plt.plot(ph_range, alpha1, label = 'Alpha 1')
    plt.xlabel('pH')
    plt.ylabel('Alpha')
    plt.title('Alpha Diagram')
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot(ph_range, logH, label = 'log H')
    plt.plot(ph_range, logOH, label = 'log OH')
    plt.plot(ph_range, logC_alpha0, label = 'logC: Alpha 0')
    plt.plot(ph_range, logC_alpha1, label = 'logC: Alpha 1')
    plt.xlabel('pH')
    plt.ylabel('Log C')
    plt.title('Log C vs. pH')
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(ph_range, buffer)
    plt.xlabel('pH')
    plt.ylabel('Buffer Intensity')
    plt.title('Buffer Intensity')

    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return img

def plot_diprotic(concentration, pka1, pka2, ph_range):
    ka1 = 10**-pka1
    ka2 = 10**-pka2
    concentration_H_diprotic = 10**-ph_range
    concentration_OH_diprotic = 10**-(14-ph_range)
    logH_diprotic = np.log10(concentration_H_diprotic)
    logOH_diprotic = np.log10(concentration_OH_diprotic)
    alpha0_diprotic = 1/(1+(ka1/concentration_H_diprotic)+(ka1*ka2/concentration_H_diprotic**2))
    alpha1_diprotic = 1/(1+concentration_H_diprotic/ka1+ka2/concentration_H_diprotic)
    alpha2 = 1/(concentration_H_diprotic**2/ka1*ka2+concentration_H_diprotic/ka2+1)
    logC_alpha0_diprotic = np.log10(concentration*alpha0_diprotic)
    logC_alpha1_diprotic = np.log10(concentration*alpha1_diprotic)
    logC_alpha2 = np.log10(concentration*alpha2)
    buffer_diprotic = 2.303*concentration*(alpha0_diprotic*alpha1_diprotic+4*alpha0_diprotic*alpha2+alpha2)

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.plot(ph_range, alpha0_diprotic, label='Alpha 0')
    plt.plot(ph_range, alpha1_diprotic, label='Alpha 1')
    plt.plot(ph_range, alpha2, label='Alpha 2')
    plt.xlabel('pH')
    plt.ylabel('Alpha')
    plt.title('Alpha Diagram')
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot(ph_range, logC_alpha0_diprotic, label='logC: Alpha 0')
    plt.plot(ph_range, logC_alpha1_diprotic, label='logC: Alpha 1')
    plt.plot(ph_range, logC_alpha2, label='logC: Alpha 2')
    plt.plot(ph_range, logOH_diprotic, label='Log H')
    plt.plot(ph_range, logOH_diprotic, label='Log OH')
    plt.xlabel('pH')
    plt.ylabel('Log C')
    plt.title('Log C vs. pH')
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(ph_range, buffer_diprotic)
    plt.xlabel('pH')
    plt.ylabel('Buffer Intensity')
    plt.title('Buffer Intensity')

    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            if 'monoprotic_concentration' in request.form:
                concentration = float(request.form['monoprotic_concentration'])
                pka = float(request.form['monoprotic_pka'])
                ph_range = np.arange(0, 14, 0.1)
                img = plot_monoprotic(concentration, pka, ph_range)
            elif 'diprotic_concentration' in request.form:
                concentration = float(request.form['diprotic_concentration'])
                pka1 = float(request.form['diprotic_pka1'])
                pka2 = float(request.form['diprotic_pka2'])
                ph_range = np.arange(0, 14, 0.1)
                img = plot_diprotic(concentration, pka1, pka2, ph_range)
            else:
                return jsonify({'error': 'Unknown form submission'})

            # Display the image in the browser
            return send_file(img, mimetype='image/png', as_attachment=True, download_name='plot.png')

        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


#This is the website to use
#http://127.0.0.1:5000/