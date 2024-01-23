
# Import required libraries
from flask import Flask, request, render_template, session, redirect, url_for, send_file
import subprocess
import os
import shutil

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'random_secret_key'

# Define the homepage route
@app.route('/')
def index():
    # Render the homepage template
    return render_template('index.html')

# Define the training route
@app.route('/train', methods=['POST'])
def train():
    # Retrieve data from the form
    data_path = request.files['data'].filename
    config_path = request.files['config'].filename

    # Validate the data
    if not os.path.isfile(data_path):
        return 'Invalid data file.', 400
    if not os.path.isfile(config_path):
        return 'Invalid config file.', 400

    # Save the data and config files temporarily
    session['data_path'] = data_path
    session['config_path'] = config_path

    # Create a Docker container to run the Nerfacto trainer
    print('Creating Docker container...')
    subprocess.call(['docker', 'run', '-it', '--rm', '-v', '{}:/data'.format(os.path.abspath(data_path)),
                   '-v', '{}:/config'.format(os.path.abspath(config_path)),
                   'nerfacto', 'train', '--data=/data', '--config=/config'])

    # Retrieve the training results from the Docker container
    print('Retrieving training results...')
    results_path = os.path.join(os.path.dirname(data_path), 'results')
    shutil.copytree(results_path, os.path.join(app.static_folder, 'results'))

    # Remove the temporary data and config files
    os.remove(data_path)
    os.remove(config_path)

    # Redirect to the results page
    return redirect(url_for('results'))

# Define the results route
@app.route('/results')
def results():
    # Render the results template
    return render_template('results.html', results=os.listdir(os.path.join(app.static_folder, 'results')))

# Define the download route
@app.route('/download/<file_name>')
def download(file_name):
    # Serve the file for download
    return send_file(os.path.join(app.static_folder, 'results', file_name), as_attachment=True)

# Define the about route
@app.route('/about')
def about():
    # Render the about page
    return render_template('about.html')

# Define error handling routes
@app.errorhandler(404)
def page_not_found(error):
    # Render the 404 page
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    # Render the 500 page
    return render_template('500.html'), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
