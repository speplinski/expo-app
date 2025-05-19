SCRIPT_TEMPLATE = """
import socket
import time

# Initialize server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(('0.0.0.0', {port})) 
server.listen({max_connections})

{custom_imports}

while True:
    data = node.io['spat'].get()
    spatialData = data.getSpatialLocations()

    # Extract distances
    distances = []
    for depthData in spatialData:
        distance = depthData.spatialCoordinates.z / 1000  # Convert to meters
        {custom_distance_processing}
        distances.append(distance)
                    
    if len(distances) > 0:
        {custom_data_preparation}
        
        det_arr = []
        for det in distances:
            det_arr.append(f"{{det:.1f}}")
        det_str = "|".join(det_arr)
        
        # Wait for client connection
        {debug_message}
        conn, client = server.accept()

        with conn:
            # Prepare header and data
            HLEN = {header_length}
            MESLEN = len(det_str)
            header = f"HEAD {{MESLEN}}".ljust(HLEN)
            
            # Send header
            msg = bytes(header, encoding='ascii')
            conn.sendall(msg)

            # Send data
            msg = bytes(det_str, encoding='ascii')
            conn.sendall(msg)
            
            {custom_post_processing}
"""

def generate_script(config):
    script_params = {
        'port': config.get('port', 65432),
        'max_connections': config.get('max_connections', 10),
        'header_length': config.get('header_length', 32),
        'custom_imports': config.get('custom_imports', '# No custom imports'),
        'custom_distance_processing': config.get('custom_distance_processing', '# No custom distance processing'),
        'custom_data_preparation': config.get('custom_data_preparation', '# No custom data preparation'),
        'custom_post_processing': config.get('custom_post_processing', '# No custom post-processing'),
        'debug_message': config.get('debug_mode', False) and 'node.warn(f"Waiting for client")' or '# Debug messages disabled'
    }
    
    return SCRIPT_TEMPLATE.format(**script_params)