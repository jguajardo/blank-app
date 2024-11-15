import streamlit as st
import os
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import jwt
import datetime
from io import BytesIO
import plotly.express as px
from streamlit_option_menu import option_menu

# Configuración de certificados para Apple Wallet
APPLE_CERT_PATH = 'certificates/pass_cert.pem'
APPLE_KEY_PATH = 'certificates/pass_key.pem'
APPLE_WWDR_PATH = 'certificates/wwdr.pem'

# Configuración de Google Wallet
GOOGLE_MERCHANT_ID = 'TU_MERCHANT_ID'  # Reemplaza con tu Merchant ID de Google Wallet
GOOGLE_SERVICE_ACCOUNT_EMAIL = 'TU_EMAIL_DE_SERVICIO@tu-proyecto.iam.gserviceaccount.com'  # Reemplaza con tu email de servicio
GOOGLE_PRIVATE_KEY_PATH = 'certificates/google_private_key.pem'

# Inicializar datos en session_state si no existen
if 'users' not in st.session_state:
    # Cargar datos mock de usuarios de Chile con detalles adicionales
    mock_users = {
        'name': [
            'Juan Pérez', 'María González', 'Carlos López', 'Ana Torres', 'Luis Martínez',
            'Sofía Díaz', 'Pedro Ruiz', 'Catalina Silva', 'Diego Romero', 'Valentina Reyes',
            'Andrés Fernández', 'Camila Vásquez', 'Mateo Herrera', 'Lucía Paredes', 'Felipe Soto',
            'Isabella Rojas', 'Santiago Morales', 'Emilia Castillo', 'Benjamín Ortiz', 'Paula Aguirre'
        ],
        'email': [
            'juan.perez@empresa.cl', 'maria.gonzalez@empresa.cl', 'carlos.lopez@empresa.cl',
            'ana.torres@empresa.cl', 'luis.martinez@empresa.cl', 'sofia.diaz@empresa.cl',
            'pedro.ruiz@empresa.cl', 'catalina.silva@empresa.cl', 'diego.romero@empresa.cl',
            'valentina.reyes@empresa.cl', 'andres.fernandez@empresa.cl', 'camila.vasquez@empresa.cl',
            'mateo.herrera@empresa.cl', 'lucia.paredes@empresa.cl', 'felipe.soto@empresa.cl',
            'isabella.rojas@empresa.cl', 'santiago.morales@empresa.cl', 'emilia.castillo@empresa.cl',
            'benjamin.ortiz@empresa.cl', 'paula.aguirre@empresa.cl'
        ],
        'age': [30, 22, 45, 28, 35, 26, 40, 33, 29, 31, 27, 24, 38, 34, 36, 23, 39, 25, 32, 21],
        'location': [
            'Santiago', 'Valparaíso', 'Concepción', 'La Serena', 'Temuco',
            'Santiago', 'Antofagasta', 'Vallenar', 'Punta Arenas', 'Iquique',
            'Rancagua', 'Talcahuano', 'Osorno', 'Puerto Montt', 'Arica',
            'Coyhaique', 'Chillán', 'Quillón', 'Copiapó', 'Calama'
        ],
        'points': [150, 200, 350, 120, 300, 180, 400, 250, 220, 310, 190, 230, 280, 270, 210, 160, 240, 170, 260, 140],
        'wallet_downloaded': [True, False, True, True, False, True, False, True, False, True, True, False, True, True, False, True, False, True, False, True],
        'wallet_installed': [True, False, True, True, False, True, False, True, False, True, True, False, True, True, False, True, False, True, False, True],
        'wallet_used': [120, 0, 300, 250, 0, 180, 0, 220, 0, 310, 190, 0, 280, 270, 0, 160, 0, 170, 0, 140],
        'wallets': [
            [
                {"wallet_id": "W001", "name": "Apple Wallet", "download_date": "2024-01-15",
                 "last_used": "2024-11-10", "usage_location": "Santiago", "device_type": "iPhone 12",
                 "os_version": "iOS 16.1", "wallet_balance": 500.0, "last_login": "2024-11-13"},
                {"wallet_id": "W002", "name": "Google Wallet", "download_date": "2024-02-20",
                 "last_used": "2024-10-05", "usage_location": "Valparaíso", "device_type": "Pixel 6",
                 "os_version": "Android 13", "wallet_balance": 300.0, "last_login": "2024-11-12"}
            ],
            [
                {"wallet_id": "W003", "name": "Apple Wallet", "download_date": "2024-03-12",
                 "last_used": "2024-11-12", "usage_location": "Concepción", "device_type": "iPad Pro",
                 "os_version": "iPadOS 16.1", "wallet_balance": 450.0, "last_login": "2024-11-14"}
            ],
            [
                {"wallet_id": "W004", "name": "Google Wallet", "download_date": "2024-04-18",
                 "last_used": "2024-11-08", "usage_location": "La Serena", "device_type": "Samsung Galaxy S21",
                 "os_version": "Android 12", "wallet_balance": 350.0, "last_login": "2024-11-11"}
            ],
            # 17 listas vacías para completar 20 elementos
            [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
        ],
        'interactions': [
            [
                {"date": "2024-05-20", "action": "Compra", "amount": 150.0, "location": "Santiago",
                 "transaction_id": "T001", "device": "iPhone 12", "transaction_type": "Compra en tienda",
                 "payment_method": "Tarjeta de Crédito"},
                {"date": "2024-06-15", "action": "Redención de puntos", "amount": 100.0, "location": "Santiago",
                 "transaction_id": "T002", "device": "iPhone 12", "transaction_type": "Redención", "payment_method": "Saldo Wallet"}
            ],
            [
                {"date": "2024-07-10", "action": "Compra", "amount": 200.0, "location": "Valparaíso",
                 "transaction_id": "T003", "device": "Pixel 6", "transaction_type": "Compra en línea",
                 "payment_method": "Google Pay"}
            ],
            [
                {"date": "2024-08-05", "action": "Compra", "amount": 250.0, "location": "Concepción",
                 "transaction_id": "T004", "device": "iPad Pro", "transaction_type": "Compra en tienda",
                 "payment_method": "Apple Pay"},
                {"date": "2024-09-12", "action": "Redención de puntos", "amount": 150.0, "location": "Concepción",
                 "transaction_id": "T005", "device": "iPad Pro", "transaction_type": "Redención", "payment_method": "Saldo Wallet"}
            ],
            # 17 listas vacías para completar 20 elementos
            [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
        ]
    }
    st.session_state.users = pd.DataFrame(mock_users)

if 'segments' not in st.session_state:
    # Añadir datos mock de segmentos
    st.session_state.segments = {
        'Clientes Frecuentes': st.session_state.users[st.session_state.users['points'] > 200].to_dict('records'),
        'Nuevos Usuarios': st.session_state.users[st.session_state.users['points'] <= 200].to_dict('records'),
        'Usuarios Activos': st.session_state.users[st.session_state.users['wallet_installed'] == True].to_dict('records'),
    }

if 'campaigns' not in st.session_state:
    # Añadir datos mock de campañas
    st.session_state.campaigns = {
        'Campaña Verano': {
            "description": "Promoción especial de verano.",
            "segments": ['Clientes Frecuentes', 'Nuevos Usuarios'],
            "scheduled_date": "2024-12-01",
            "distribution_channels": ["Email", "SMS"],
            "status": "En Progreso"
        },
        'Campaña Navidad': {
            "description": "Ofertas navideñas exclusivas.",
            "segments": ['Clientes Frecuentes'],
            "scheduled_date": "2024-12-20",
            "distribution_channels": ["Email", "Redes Sociales"],
            "status": "Programada"
        },
    }

if 'push_notifications' not in st.session_state:
    # Añadir datos mock de notificaciones push
    st.session_state.push_notifications = [
        {
            "notification": {
                "title": "¡Oferta de Verano!",
                "message": "Disfruta de un 20% de descuento en todas las compras este verano.",
                "campaigns": ["Campaña Verano"]
            },
            "users": st.session_state.segments['Clientes Frecuentes']
        },
        {
            "notification": {
                "title": "Bienvenido a la Empresa",
                "message": "Gracias por unirte a nosotros. Aquí tienes un bono de bienvenida.",
                "campaigns": ["Campaña Bienvenida"]
            },
            "users": st.session_state.segments['Nuevos Usuarios']
        }
    ]

if 'api_connections' not in st.session_state:
    st.session_state.api_connections = {
        'Google Analytics': 'GA-123456789'
    }

if 'loyalty_program' not in st.session_state:
    st.session_state.loyalty_program = {
        'rewards': [
            {"reward_id": 1, "description": "Descuento del 10% en la próxima compra", "points_required": 100},
            {"reward_id": 2, "description": "Producto gratuito", "points_required": 200}
        ],
        'redemptions': [
            {"redemption_id": 1, "user_email": "juan.perez@empresa.cl", "reward_id": 1, "date": "2024-10-15"},
        ]
    }

if 'support_tickets' not in st.session_state:
    st.session_state.support_tickets = [
        {"ticket_id": 1, "user_email": "juan.perez@empresa.cl", "issue": "Problema con la redención de puntos", "status": "Abierto", "date": "2024-11-01"},
    ]

if 'ab_testing' not in st.session_state:
    st.session_state.ab_testing = {
        'tests': [
            {"test_id": 1, "campaign": "Campaña Verano", "variant": "A", "description": "Email con descuento del 20%", "metrics": {"open_rate": 0.25, "click_rate": 0.15}},
            {"test_id": 2, "campaign": "Campaña Verano", "variant": "B", "description": "Email con descuento del 25%", "metrics": {"open_rate": 0.30, "click_rate": 0.18}},
            # Añadir más pruebas A/B relacionadas con otras campañas y segmentos
            {"test_id": 3, "campaign": "Campaña Navidad", "variant": "A", "description": "Email con oferta navideña del 15%", "metrics": {"open_rate": 0.20, "click_rate": 0.10}},
            {"test_id": 4, "campaign": "Campaña Navidad", "variant": "B", "description": "Email con oferta navideña del 20%", "metrics": {"open_rate": 0.28, "click_rate": 0.16}},
        ]
    }

# Función para convertir colores de hexadecimal a tupla RGB
def parse_color(color_str):
    color_str = color_str.lstrip('#')
    return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))

# Función para crear una vista previa del pase
def create_preview(design, data, images):
    # Crear una imagen en blanco para el frente y el reverso
    front = Image.new('RGB', (300, 600), color=parse_color(design.get('background_color', '#FFFFFF')))
    back = Image.new('RGB', (300, 600), color=parse_color(design.get('background_color', '#FFFFFF')))

    draw_front = ImageDraw.Draw(front)
    draw_back = ImageDraw.Draw(back)

    # Definir fuentes (asegúrate de tener la fuente Arial o cambia a una disponible)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Dibujar campos primarios en el frente
    primary_label = design.get('primary_field_label', 'Nombre')
    primary_value = data.get('name', 'Juan Pérez')
    draw_front.text((20, 20), f"{primary_label}: {primary_value}", fill=parse_color(design.get('foreground_color', '#000000')), font=font)

    # Dibujar campos secundarios
    y_offset = 70
    for field in design.get('secondary_fields', []):
        label = field['label']
        value = field['value']
        draw_front.text((20, y_offset), f"{label}: {value}", fill=parse_color(design.get('foreground_color', '#000000')), font=font)
        y_offset += 40

    # Dibujar campos auxiliares
    for field in design.get('auxiliary_fields', []):
        label = field['label']
        value = field['value']
        draw_front.text((20, y_offset), f"{label}: {value}", fill=parse_color(design.get('foreground_color', '#000000')), font=font)
        y_offset += 40

    # Dibujar código de barras si está habilitado
    if design.get('barcode', {}).get('enable', False):
        barcode_message = design['barcode']['message']
        # Simplificación: dibujar el mensaje del código de barras como texto
        draw_front.text((20, y_offset), f"Barcode: {barcode_message}", fill=parse_color(design.get('foreground_color', '#000000')), font=font)
        y_offset += 40

    # Dibujar imágenes en el frente
    if 'logo.png' in images:
        logo = Image.open(images['logo.png']).convert("RGBA")
        logo = logo.resize((80, 80))
        front.paste(logo, (200, 500), logo)
    if 'icon.png' in images:
        icon = Image.open(images['icon.png']).convert("RGBA")
        icon = icon.resize((60, 60))
        front.paste(icon, (20, 500), icon)

    # Dibujar campos en la parte posterior
    y_offset_back = 20
    for field in design.get('back_fields', []):
        label = field['label']
        value = field['value']
        draw_back.text((20, y_offset_back), f"{label}: {value}", fill=parse_color(design.get('foreground_color', '#000000')), font=font)
        y_offset_back += 40

    # Dibujar imágenes en el reverso
    if 'logo.png' in images:
        logo_back = Image.open(images['logo.png']).convert("RGBA")
        logo_back = logo_back.resize((80, 80))
        back.paste(logo_back, (200, 500), logo_back)
    if 'icon.png' in images:
        icon_back = Image.open(images['icon.png']).convert("RGBA")
        icon_back = icon_back.resize((60, 60))
        back.paste(icon_back, (20, 500), icon_back)

    return front, back

# Función para crear un marco simulado de teléfono
def create_phone_frame(pase_image):
    # Crear un marco con borde y esquinas redondeadas
    frame_width, frame_height = pase_image.size
    border_size = 10
    corner_radius = 30

    # Crear una imagen con transparencia
    frame = Image.new('RGBA', (frame_width + 2*border_size, frame_height + 2*border_size), (255,255,255,0))
    draw = ImageDraw.Draw(frame)

    # Dibujar un rectángulo con bordes redondeados
    rect = [border_size, border_size, frame_width + border_size, frame_height + border_size]
    draw.rounded_rectangle(rect, radius=corner_radius, outline="black", width=border_size)

    # Pegar la imagen del pase en el centro del marco
    frame.paste(pase_image, (border_size, border_size), pase_image.convert("RGBA"))

    return frame

# Función para crear un pase de Apple Wallet
def create_apple_pass(pass_type, data, images, design):
    # Aquí deberías implementar la lógica para crear un archivo .pkpass
    # utilizando los certificados y la estructura JSON requerida por Apple.
    # Esta implementación es una simplificación y no genera un pase válido.
    pass_info = {
        "description": data.get("description", ""),
        "formatVersion": 1,
        "organizationName": "Empresa Chilena S.A.",
        "passTypeIdentifier": "pass.com.empresachilena.tupase",  # Reemplaza con tu Pass Type ID
        "serialNumber": data.get("serial_number", "123456"),
        "teamIdentifier": "YOUR_TEAM_ID",  # Reemplaza con tu Team ID de Apple
        "foregroundColor": design.get('foreground_color', '#000000'),
        "backgroundColor": design.get('background_color', '#FFFFFF'),
        "labelColor": design.get('label_color', '#000000'),
        "logoText": data.get("name", "Nombre"),
        "generic": {
            "primaryFields": [
                {
                    "key": "name",
                    "label": design.get('primary_field_label', 'Nombre'),
                    "value": data.get("name", "")
                }
            ],
            "secondaryFields": design.get('secondary_fields', []),
            "auxiliaryFields": design.get('auxiliary_fields', []),
            "backFields": design.get('back_fields', []),
            "barcode": design.get('barcode', {})
        }
    }

    # Convertir pass_info a JSON
    pass_json = json.dumps(pass_info, indent=4)

    # Guardar el archivo JSON (esto es solo una representación)
    os.makedirs("generated_passes", exist_ok=True)
    pass_path = f"generated_passes/{pass_type}_{data.get('serial_number', '123456')}.json"
    with open(pass_path, "w") as f:
        f.write(pass_json)

    # Retornar la ruta del archivo (en una implementación real, deberías generar el .pkpass)
    return pass_path

# Función para crear un pase de Google Wallet
def create_google_pass(pass_type, data, images, design):
    # Aquí deberías implementar la lógica para crear un pase para Google Wallet
    # utilizando la API correspondiente y la autenticación JWT.
    # Esta implementación es una simplificación y no genera un pase válido.

    # Crear el payload del JWT
    payload = {
        "iss": GOOGLE_SERVICE_ACCOUNT_EMAIL,
        "aud": "https://walletobjects.googleapis.com/",
        "typ": "savetoandroidpay",
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        "payload": {
            "genericObjects": [
                {
                    "id": f"{GOOGLE_MERCHANT_ID}.{data.get('serial_number', '123456')}",
                    "classId": f"{GOOGLE_MERCHANT_ID}.{pass_type.lower().replace(' ', '_')}",
                    "state": "active",
                    "genericType": pass_type.lower().replace(' ', '_'),
                    "heroImage": {
                        "sourceUri": {
                            "uri": "https://tu-servidor.com/images/hero_image.png"  # Reemplaza con la URL de tu imagen
                        }
                    },
                    "logo": {
                        "sourceUri": {
                            "uri": "https://tu-servidor.com/images/logo.png"  # Reemplaza con la URL de tu logo
                        }
                    },
                    "title": data.get("name", ""),
                    "subtitle": data.get("description", ""),
                    "textModulesData": [
                        {
                            "header": field['label'],
                            "body": field['value']
                        } for field in design.get('secondary_fields', [])
                    ]
                }
            ]
        }
    }

    # Leer la clave privada
    try:
        with open(GOOGLE_PRIVATE_KEY_PATH, 'r') as key_file:
            private_key = key_file.read()
    except FileNotFoundError:
        st.error("Clave privada de Google Wallet no encontrada.")
        return "#"

    # Generar el token JWT
    token = jwt.encode(payload, private_key, algorithm='RS256')

    # Generar el enlace para guardar en Google Wallet
    save_url = f"https://pay.google.com/gp/v/save/{token}"

    return save_url

# Función para enviar notificaciones push (Simulación)
def send_push_notification(notification, segment_users):
    # Esta función debería integrarse con un servicio de notificaciones push real
    # como Firebase Cloud Messaging (FCM), OneSignal, etc.
    # Aquí se simula enviando notificaciones.
    for user in segment_users:
        st.write(f"Enviando notificación a {user['name']} ({user['email']}): {notification['message']}")

# Función para asignar puntos a usuarios
def assign_points(user_email, points):
    if not st.session_state.users.empty:
        st.session_state.users.loc[st.session_state.users['email'] == user_email, 'points'] += points
        st.success(f"Se han asignado {points} puntos a {user_email}.")
    else:
        st.warning("No hay usuarios disponibles.")

# Función para redimir puntos
def redeem_points(user_email, points):
    user = st.session_state.users[st.session_state.users['email'] == user_email]
    if not user.empty:
        current_points = user['points'].values[0]
        if current_points >= points:
            st.session_state.users.loc[st.session_state.users['email'] == user_email, 'points'] -= points
            st.success(f"Se han redimido {points} puntos de {user_email}.")
        else:
            st.error("Puntos insuficientes para redimir.")
    else:
        st.error("Usuario no encontrado.")

# Función para generar tarjetas personalizadas usando HTML y CSS
def create_card(title, content, icon, color):
    card_html = f"""
    <div style="
        background-color: {color};
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin: 10px;
    ">
        <div style="font-size: 40px;">{icon}</div>
        <h3 style="margin-bottom: 10px;">{title}</h3>
        <p style="font-size: 24px; margin: 0;">{content}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# Función para generar gráficos de analítica usando Plotly
def generar_graficos():
    st.subheader("Análisis de Usuarios")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribución de Edad de Usuarios")
        fig1 = px.histogram(st.session_state.users, x='age', nbins=10, title='Distribución de Edad',
                           labels={'age':'Edad'}, color_discrete_sequence=['#4B8BBE'])
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### Distribución Geográfica de Usuarios")
        location_counts = st.session_state.users['location'].value_counts().reset_index()
        location_counts.columns = ['location', 'count']
        fig2 = px.pie(location_counts, names='location', values='count', title='Distribución Geográfica',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Análisis de Puntos de Fidelización")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Distribución de Puntos")
        fig3 = px.bar(st.session_state.users, x='name', y='points', title='Distribución de Puntos',
                     labels={'points':'Puntos', 'name':'Usuario'}, color='points',
                     color_continuous_scale='Viridis')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("#### Evolución de Puntos por Edad")
        # Crear un DataFrame ordenado por edad
        df_evol = st.session_state.users.sort_values('age')
        fig4 = px.line(df_evol, x='age', y='points', markers=True, title='Evolución de Puntos por Edad',
                      labels={'age':'Edad', 'points':'Puntos'}, color='location')
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### Análisis de Wallets")
    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown("#### Wallets Descargadas vs Instaladas")
        wallets = st.session_state.users[['wallet_downloaded', 'wallet_installed']]
        wallets_counts = wallets.sum().reset_index()
        wallets_counts.columns = ['Estado', 'Cantidad']
        fig5 = px.pie(wallets_counts, names='Estado', values='Cantidad',
                     title='Wallets Descargadas vs Instaladas',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown("#### Wallets Usadas por Usuarios")
        used_wallets = st.session_state.users[st.session_state.users['wallet_used'] > 0]
        fig6 = px.bar(used_wallets, x='name', y='wallet_used', title='Wallets Usadas por Usuarios',
                     labels={'wallet_used':'Uso de Wallet (número de transacciones)', 'name':'Usuario'},
                     color='wallet_used', color_continuous_scale='Portland')
        st.plotly_chart(fig6, use_container_width=True)

    with col7:
        st.markdown("#### Saldo Promedio en Wallets")
        # Calcular el saldo promedio por wallet
        wallet_balances = []
        for wallets_list in st.session_state.users['wallets']:
            for wallet in wallets_list:
                wallet_balances.append(wallet['wallet_balance'])
        if wallet_balances:
            avg_balance = sum(wallet_balances) / len(wallet_balances)
            st.metric(label="Saldo Promedio en Wallets", value=f"${avg_balance:.2f}")
        else:
            st.write("No hay datos de saldos disponibles.")

    st.markdown("### Análisis de Segmentación")
    if st.session_state.segments:
        num_segments = len(st.session_state.segments)
        st.markdown(f"**Número de Segmentos:** {num_segments}")
        st.markdown("#### Usuarios por Segmento")
        segments_counts = {seg: len(users) for seg, users in st.session_state.segments.items()}
        segments_counts_df = pd.DataFrame(list(segments_counts.items()), columns=['Segmento', 'Cantidad de Usuarios'])
        fig7 = px.bar(segments_counts_df, x='Segmento', y='Cantidad de Usuarios', 
                     title='Usuarios por Segmento', labels={'Segmento':'Segmento', 'Cantidad de Usuarios':'Cantidad de Usuarios'},
                     color='Segmento', color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig7, use_container_width=True)
        
        # **Añadido**: Tabla de Segmentos y Cantidad de Usuarios
        st.markdown("#### Tabla de Segmentos")
        st.dataframe(segments_counts_df)

    st.markdown("### Análisis de Campañas")
    if st.session_state.campaigns:
        total_campaigns = len(st.session_state.campaigns)
        completed_campaigns = len([camp for camp in st.session_state.campaigns.values() if camp['status'] == 'Completada'])
        in_progress_campaigns = len([camp for camp in st.session_state.campaigns.values() if camp['status'] == 'En Progreso'])
        scheduled_campaigns = total_campaigns - completed_campaigns - in_progress_campaigns

        # Campañas por Estado
        estados = ['Programada', 'En Progreso', 'Completada']
        counts = [scheduled_campaigns, in_progress_campaigns, completed_campaigns]
        campañas_estado_df = pd.DataFrame({'Estado de la Campaña': estados, 'Cantidad de Campañas': counts})

        st.markdown("#### Campañas por Estado")
        fig8 = px.pie(campañas_estado_df, names='Estado de la Campaña', values='Cantidad de Campañas',
                     title='Campañas por Estado', color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig8, use_container_width=True)

        # Campañas por Segmento
        all_segments = []
        for camp in st.session_state.campaigns.values():
            all_segments.extend(camp['segments'])
        segment_counts = pd.Series(all_segments).value_counts().reset_index()
        segment_counts.columns = ['Segmento', 'Cantidad de Campañas']

        st.markdown("#### Campañas por Segmento")
        fig9 = px.bar(segment_counts, x='Segmento', y='Cantidad de Campañas',
                     title='Campañas por Segmento',
                     labels={'Segmento':'Segmento', 'Cantidad de Campañas':'Cantidad de Campañas'},
                     color='Segmento', color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig9, use_container_width=True)
        
        # **Añadido**: Tabla de Campañas por Segmento
        st.markdown("#### Tabla de Campañas por Segmento")
        st.dataframe(segment_counts)

    st.markdown("### Análisis de Notificaciones Push")
    if st.session_state.push_notifications:
        total_notifications = len(st.session_state.push_notifications)
        unique_campaigns = set()
        for notif in st.session_state.push_notifications:
            unique_campaigns.update(notif['notification']['campaigns'])
        total_campaigns_notif = len(unique_campaigns)

        st.markdown(f"**Total de Notificaciones Enviadas:** {total_notifications}")
        st.markdown(f"**Total de Campañas Notificadas:** {total_campaigns_notif}")

        # Notificaciones por Campaña
        campaigns_notif = {}
        for notif in st.session_state.push_notifications:
            for camp in notif['notification']['campaigns']:
                campaigns_notif[camp] = campaigns_notif.get(camp, 0) + 1

        campaigns_notif_df = pd.DataFrame(list(campaigns_notif.items()), columns=['Campaña', 'Cantidad de Notificaciones'])

        st.markdown("#### Notificaciones por Campaña")
        fig10 = px.pie(campaigns_notif_df, names='Campaña', values='Cantidad de Notificaciones',
                      title='Notificaciones por Campaña',
                      color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig10, use_container_width=True)
        
        # **Añadido**: Tabla de Notificaciones por Campaña
        st.markdown("#### Tabla de Notificaciones por Campaña")
        st.dataframe(campaigns_notif_df)

    st.markdown("### Análisis de Recompensas y Redenciones")
    if st.session_state.loyalty_program:
        # Recompensas
        st.markdown("#### Recompensas Disponibles")
        if st.session_state.loyalty_program['rewards']:
            df_rewards = pd.DataFrame(st.session_state.loyalty_program['rewards'])
            st.dataframe(df_rewards)
        else:
            st.write("No hay recompensas disponibles.")

        # Redenciones
        st.markdown("#### Historial de Redenciones")
        if st.session_state.loyalty_program['redemptions']:
            df_redemptions = pd.DataFrame(st.session_state.loyalty_program['redemptions'])
            st.dataframe(df_redemptions)
        else:
            st.write("No hay redenciones registradas.")

    st.markdown("### Análisis de Soporte al Cliente")
    if st.session_state.support_tickets:
        st.markdown("#### Tickets de Soporte")
        df_tickets = pd.DataFrame(st.session_state.support_tickets)
        st.dataframe(df_tickets)
    else:
        st.write("No hay tickets de soporte.")

    # Función para crear reportes descargables
    def create_report():
        try:
            # Crear un DataFrame con todas las métricas
            report_data = {
                'Total Usuarios': [len(st.session_state.users)],
                'Usuarios Activos': [len(st.session_state.users[st.session_state.users['wallet_installed'] == True])],
                'Campañas Activas': [len([camp for camp in st.session_state.campaigns.values() if camp['status'] == 'En Progreso'])],
                'Notificaciones Enviadas': [len(st.session_state.push_notifications)],
                'Recompensas Disponibles': [len(st.session_state.loyalty_program['rewards'])],
                'Redenciones Registradas': [len(st.session_state.loyalty_program['redemptions'])],
                'Tickets de Soporte': [len(st.session_state.support_tickets)],
                'Tests A/B': [len(st.session_state.ab_testing['tests'])]
            }
            df_report = pd.DataFrame(report_data)

            # Convertir a Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_report.to_excel(writer, index=False, sheet_name='Resumen')
                st.session_state.users.to_excel(writer, index=False, sheet_name='Usuarios')
                if st.session_state.campaigns:
                    df_campaigns = pd.DataFrame(st.session_state.campaigns).T
                    df_campaigns.reset_index(inplace=True)
                    df_campaigns.rename(columns={'index': 'Nombre de la Campaña'}, inplace=True)
                    df_campaigns.to_excel(writer, index=False, sheet_name='Campañas')
                if st.session_state.push_notifications:
                    notif_list = []
                    for notif in st.session_state.push_notifications:
                        notif_list.append({
                            "Título": notif['notification']['title'],
                            "Mensaje": notif['notification']['message'],
                            "Campañas": ", ".join(notif['notification']['campaigns']),
                            "Usuarios Destinatarios": len(notif['users'])
                        })
                    df_notifs = pd.DataFrame(notif_list)
                    df_notifs.to_excel(writer, index=False, sheet_name='Notificaciones')
                if st.session_state.loyalty_program:
                    df_rewards = pd.DataFrame(st.session_state.loyalty_program['rewards'])
                    df_rewards.to_excel(writer, index=False, sheet_name='Recompensas')
                    df_redemptions = pd.DataFrame(st.session_state.loyalty_program['redemptions'])
                    df_redemptions.to_excel(writer, index=False, sheet_name='Redenciones')
                if st.session_state.support_tickets:
                    df_tickets = pd.DataFrame(st.session_state.support_tickets)
                    df_tickets.to_excel(writer, index=False, sheet_name='Tickets de Soporte')
                if st.session_state.ab_testing:
                    df_ab = pd.DataFrame(st.session_state.ab_testing['tests'])
                    df_ab.to_excel(writer, index=False, sheet_name='A/B Testing')

            excel_data = output.getvalue()
            st.download_button(
                label="Descargar Reporte Completo (Excel)",
                data=excel_data,
                file_name="reporte_captain_wallet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error al generar el reporte: {e}")

def main():
    # Configuración de la página
    st.set_page_config(page_title="Captain Wallet", layout="wide", page_icon="💼")

    # Eliminar Dark Mode y usar colores claros
    st.markdown("""
    <style>
    /* Estilos para un tema claro */
    body {
        background-color: #FFFFFF;
        color: #000000;
    }
    .stApp {
        background-color: #FFFFFF;
    }
    .css-1d391kg, .css-1adrfps, .css-1yh6m8x {
        color: #000000;
    }
    /* Botones */
    .css-1emrehy.edgvbvh3 {
        background-color: #4B8BBE;
        color: white;
    }
    /* Tableros y Tarjetas */
    .css-1aumxhk.edgvbvh3 {
        background-color: #F5F5F5;
        color: #000000;
    }
    /* Sidebar */
    .css-1lcbmhc.e1fqkh3o3 {
        background-color: #F5F5F5;
        color: #000000;
    }
    /* Expander */
    .streamlit-expanderHeader {
        color: #4B8BBE;
    }
    </style>
    """, unsafe_allow_html=True)

    # Opción de Menú Lateral usando streamlit-option-menu
    with st.sidebar:
        selected = option_menu(
            menu_title="Captain Wallet",  # Título del menú
            options=["🏠 Home", "📥 Importar Usuarios", "📊 Segmentación", "📢 Campañas", 
                     "📬 Notificaciones Push", "⚙️ Configuración", "🔗 Conexiones con API", 
                     "🎨 Diseñador de Pases", "📈 Analítica", "🛠️ Soporte", "📑 Reportes", 
                     "🔬 A/B Testing", "🔍 Buscar Wallet"],
            icons=["house", "cloud-upload", "people", "bullhorn", "envelope", 
                   "gear", "link", "palette", "bar-chart", "tools", "file-earmark-text", 
                   "microscope", "search"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical"
        )

    # Home Dashboard
    if selected == "🏠 Home":
        st.markdown("<h1 style='color:#000000;'>Captain Wallet</h1>", unsafe_allow_html=True)
        st.markdown("### Dashboard Resumen")

        # Crear tarjetas con información general
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            create_card(title="Total Usuarios", content=str(len(st.session_state.users)),
                       icon="👥", color="#4B8BBE")

        with col2:
            active_users = len(st.session_state.users[st.session_state.users['wallet_installed'] == True])
            create_card(title="Usuarios Activos", content=str(active_users),
                       icon="✅", color="#7FCDCD")

        with col3:
            active_campaigns = len([camp for camp in st.session_state.campaigns.values() if camp['status'] == 'En Progreso'])
            create_card(title="Campañas Activas", content=str(active_campaigns),
                       icon="📈", color="#FFC75F")

        with col4:
            total_push = len(st.session_state.push_notifications)
            create_card(title="Notificaciones Enviadas", content=str(total_push),
                       icon="📬", color="#FF6F61")

        # Gráficos Resumidos
        st.markdown("### Resumen de Analítica")
        col5, col6 = st.columns(2)

        with col5:
            fig1 = px.bar(x=['Usuarios Activos', 'Campañas Activas', 'Notificaciones Enviadas'],
                         y=[active_users, active_campaigns, total_push],
                         labels={'x':'Categoría', 'y':'Cantidad'},
                         title='Resumen General',
                         color=['#4B8BBE', '#FFC75F', '#FF6F61'])
            st.plotly_chart(fig1, use_container_width=True)

        with col6:
            location_counts = st.session_state.users['location'].value_counts().reset_index()
            location_counts.columns = ['location', 'count']
            fig2 = px.pie(location_counts, names='location', values='count', title='Distribución Geográfica',
                         color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig2, use_container_width=True)

    # Importar Usuarios
    elif selected == "📥 Importar Usuarios":
        st.header("Importar Usuarios")
        st.markdown("### Cargar un archivo de usuarios (CSV o Excel)")

        uploaded_file = st.file_uploader("Selecciona un archivo CSV o Excel", type=["csv", "xlsx"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                # Verificar columnas necesarias
                required_columns = ['name', 'email', 'age', 'location', 'points', 'wallet_downloaded', 'wallet_installed', 'wallet_used']
                if all(column in df.columns for column in required_columns):
                    # Añadir datos mock para wallets e interacciones si no existen
                    if 'wallets' not in df.columns:
                        df['wallets'] = [[] for _ in range(len(df))]
                    if 'interactions' not in df.columns:
                        df['interactions'] = [[] for _ in range(len(df))]

                    # Asegurarse de que 'wallets' y 'interactions' tengan listas correctamente formateadas
                    st.session_state.users = df
                    st.success("Usuarios importados exitosamente!")
                    # Mostrar la tabla con wallets e interacciones correctamente formateadas
                    st.markdown("### Lista de Usuarios")
                    for idx, row in st.session_state.users.iterrows():
                        with st.expander(f"{row['name']} ({row['email']})"):
                            # Mostrar detalles del usuario en una tabla
                            user_details = {
                                "Edad": row['age'],
                                "Ubicación": row['location'],
                                "Puntos": row['points']
                            }
                            st.table(pd.DataFrame([user_details]))

                            # Mostrar Wallets Asociadas en una tabla
                            st.markdown("##### Wallets Asociadas")
                            if row['wallets']:
                                wallets_df = pd.DataFrame(row['wallets'])
                                st.table(wallets_df)
                            else:
                                st.write("No hay wallets asociadas.")

                            # Mostrar Interacciones en una tabla
                            st.markdown("##### Interacciones")
                            if row['interactions']:
                                interactions_df = pd.DataFrame(row['interactions'])
                                st.table(interactions_df)
                            else:
                                st.write("No hay interacciones registradas.")
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
        else:
            st.info("Usando datos mock de usuarios de Chile:")
            # Mostrar la tabla con wallets e interacciones correctamente formateadas
            st.markdown("### Lista de Usuarios")
            for idx, row in st.session_state.users.iterrows():
                with st.expander(f"{row['name']} ({row['email']})"):
                    # Mostrar detalles del usuario en una tabla
                    user_details = {
                        "Edad": row['age'],
                        "Ubicación": row['location'],
                        "Puntos": row['points']
                    }
                    st.table(pd.DataFrame([user_details]))

                    # Mostrar Wallets Asociadas en una tabla
                    st.markdown("##### Wallets Asociadas")
                    if row['wallets']:
                        wallets_df = pd.DataFrame(row['wallets'])
                        st.table(wallets_df)
                    else:
                        st.write("No hay wallets asociadas.")

                    # Mostrar Interacciones en una tabla
                    st.markdown("##### Interacciones")
                    if row['interactions']:
                        interactions_df = pd.DataFrame(row['interactions'])
                        st.table(interactions_df)
                    else:
                        st.write("No hay interacciones registradas.")

    # Segmentación
    elif selected == "📊 Segmentación":
        st.header("Segmentación de Usuarios")
        st.markdown("### Crear y Gestionar Segmentos")

        if st.session_state.users.empty:
            st.warning("No hay usuarios importados. Por favor, ve a '📥 Importar Usuarios' para agregar usuarios.")
        else:
            with st.form("segment_form"):
                segment_name = st.text_input("Nombre del Segmento")
                age_filter = st.selectbox("Filtrar por Edad", ["Todos", "Mayor de 25", "Menor de 25"])
                location_filter = st.selectbox("Filtrar por Ubicación", ["Todos"] + sorted(st.session_state.users['location'].unique().tolist()))
                submitted = st.form_submit_button("Crear Segmento")

            if submitted:
                if segment_name:
                    # Aplicar filtros
                    filtered_users = st.session_state.users.copy()
                    if age_filter == "Mayor de 25":
                        filtered_users = filtered_users[filtered_users['age'] > 25]
                    elif age_filter == "Menor de 25":
                        filtered_users = filtered_users[filtered_users['age'] < 25]

                    if location_filter != "Todos":
                        filtered_users = filtered_users[filtered_users['location'] == location_filter]

                    # Guardar segmento
                    st.session_state.segments[segment_name] = filtered_users.to_dict('records')
                    st.success(f"Segmento '{segment_name}' creado exitosamente!")
                else:
                    st.error("Por favor, ingresa un nombre para el segmento.")

            # Filtro de búsqueda en segmentos
            search_segment = st.text_input("Buscar Segmento por Nombre")
            if search_segment:
                filtered_segments = {k: v for k, v in st.session_state.segments.items() if search_segment.lower() in k.lower()}
            else:
                filtered_segments = st.session_state.segments

            # Mostrar segmentos existentes en tablas
            if filtered_segments:
                st.markdown("### Segmentos Existentes")
                for seg_name, users in filtered_segments.items():
                    st.markdown(f"#### Segmento: {seg_name} ({len(users)} usuarios)")
                    users_df = pd.DataFrame(users)
                    st.table(users_df[['name', 'email', 'age', 'location', 'points']])
            else:
                st.write("No se encontraron segmentos que coincidan con la búsqueda.")

    # Campañas
    elif selected == "📢 Campañas":
        st.header("Gestión de Campañas")
        st.markdown("### Crear y Gestionar Campañas de Pases")

        if not st.session_state.segments:
            st.warning("No hay segmentos disponibles. Por favor, ve a '📊 Segmentación' para crear segmentos.")
        else:
            with st.form("campaign_form"):
                campaign_name = st.text_input("Nombre de la Campaña")
                selected_segments = st.multiselect("Selecciona Segmentos", list(st.session_state.segments.keys()))
                campaign_description = st.text_area("Descripción de la Campaña")
                scheduled_date = st.date_input("Fecha Programada")
                distribution_channels = st.multiselect("Canales de Distribución", ["Email", "SMS", "Redes Sociales", "App Móvil", "Sitio Web"])
                submitted = st.form_submit_button("Crear Campaña")

            if submitted:
                if campaign_name and selected_segments and distribution_channels:
                    st.session_state.campaigns[campaign_name] = {
                        "description": campaign_description,
                        "segments": selected_segments,
                        "scheduled_date": str(scheduled_date),
                        "distribution_channels": distribution_channels,
                        "status": "Programada"
                    }
                    st.success(f"Campaña '{campaign_name}' creada exitosamente!")
                else:
                    st.error("Por favor, completa todos los campos obligatorios.")

            # Filtro de búsqueda en campañas
            search_campaign = st.text_input("Buscar Campaña por Nombre")
            if search_campaign:
                filtered_campaigns = {k: v for k, v in st.session_state.campaigns.items() if search_campaign.lower() in k.lower()}
            else:
                filtered_campaigns = st.session_state.campaigns

            # Mostrar campañas existentes
            if filtered_campaigns:
                st.markdown("### Campañas Existentes")
                for camp_name, details in filtered_campaigns.items():
                    with st.expander(f"{camp_name} - {details['status']}"):
                        st.write(f"**Descripción:** {details['description']}")
                        st.write(f"**Segmentos:** {', '.join(details['segments'])}")
                        st.write(f"**Canales de Distribución:** {', '.join(details['distribution_channels'])}")
                        st.write(f"**Fecha Programada:** {details['scheduled_date']}")
                        st.write(f"**Estado:** {details['status']}")

                        # Botones para actualizar estado
                        col1, col2 = st.columns(2)
                        with col1:
                            if details['status'] not in ["En Progreso", "Completada"]:
                                if st.button(f"Iniciar {camp_name}", key=f"start_{camp_name}"):
                                    st.session_state.campaigns[camp_name]['status'] = "En Progreso"
                                    st.success(f"Campaña '{camp_name}' iniciada!")
                        with col2:
                            if details['status'] != "Completada":
                                if st.button(f"Completar {camp_name}", key=f"complete_{camp_name}"):
                                    st.session_state.campaigns[camp_name]['status'] = "Completada"
                                    st.success(f"Campaña '{camp_name}' completada!")
            else:
                st.write("No se encontraron campañas que coincidan con la búsqueda.")

    # Notificaciones Push
    elif selected == "📬 Notificaciones Push":
        st.header("Notificaciones Push")
        st.markdown("### Enviar Notificaciones a Segmentos")

        if not st.session_state.campaigns:
            st.warning("No hay campañas disponibles. Por favor, ve a '📢 Campañas' para crear campañas.")
        else:
            with st.form("push_form"):
                notification_title = st.text_input("Título de la Notificación")
                notification_message = st.text_area("Mensaje de la Notificación")
                selected_campaigns = st.multiselect("Selecciona Campañas", list(st.session_state.campaigns.keys()))
                submitted = st.form_submit_button("Enviar Notificación")

            if submitted:
                if notification_title and notification_message and selected_campaigns:
                    # Obtener usuarios de las campañas seleccionadas
                    target_users = []
                    for camp in selected_campaigns:
                        segments = st.session_state.campaigns[camp]['segments']
                        for seg in segments:
                            target_users.extend(st.session_state.segments[seg])

                    # Eliminar duplicados
                    unique_users = {user['email']: user for user in target_users}.values()

                    # Crear notificación
                    notification = {
                        "title": notification_title,
                        "message": notification_message,
                        "campaigns": selected_campaigns
                    }

                    # Guardar notificación
                    st.session_state.push_notifications.append({
                        "notification": notification,
                        "users": list(unique_users)
                    })

                    # Simular envío de notificaciones
                    send_push_notification(notification, list(unique_users))
                    st.success("Notificaciones enviadas exitosamente!")
                else:
                    st.error("Por favor, completa todos los campos obligatorios.")

            # Filtro de búsqueda en notificaciones
            search_notification = st.text_input("Buscar Notificación por Título")
            if search_notification:
                filtered_notifications = [notif for notif in st.session_state.push_notifications 
                                          if search_notification.lower() in notif['notification']['title'].lower()]
            else:
                filtered_notifications = st.session_state.push_notifications

            # Mostrar notificaciones enviadas en tablas
            if filtered_notifications:
                st.markdown("### Notificaciones Enviadas")
                notif_data = []
                for idx, notif in enumerate(filtered_notifications, 1):
                    notif_entry = {
                        "ID": idx,
                        "Título": notif['notification']['title'],
                        "Mensaje": notif['notification']['message'],
                        "Campañas": ", ".join(notif['notification']['campaigns']),
                        "Usuarios Destinatarios": len(notif['users'])
                    }
                    notif_data.append(notif_entry)
                df_notif = pd.DataFrame(notif_data)
                st.dataframe(df_notif)
            else:
                st.write("No se encontraron notificaciones que coincidan con la búsqueda.")

    # Configuración
    elif selected == "⚙️ Configuración":
        st.header("Configuración")
        st.markdown("### Gestionar Ajustes y Preferencias")

        # Submenú de Configuración
        config_options = ["General", "Seguridad", "Integraciones"]
        config_choice = st.radio("Opciones de Configuración", config_options)

        if config_choice == "General":
            st.subheader("Ajustes Generales")
            company_name = st.text_input("Nombre de la Empresa", value="Empresa Chilena S.A.")
            company_logo = st.file_uploader("Subir Logo de la Empresa", type=["png", "jpg"], key="company_logo")
            if company_logo:
                # Guardar el logo en 'static/images/company_logo.png'
                try:
                    img = Image.open(company_logo)
                    os.makedirs('static/images', exist_ok=True)
                    img.save('static/images/company_logo.png')
                    st.session_state.api_connections['company_logo'] = 'static/images/company_logo.png'
                    st.success("Logo de la empresa actualizado exitosamente!")
                except Exception as e:
                    st.error(f"Error al guardar el logo: {e}")
            st.write("Ajustes generales de la aplicación.")

        elif config_choice == "Seguridad":
            st.subheader("Ajustes de Seguridad")
            enable_two_factor = st.checkbox("Habilitar Autenticación de Dos Factores")
            if enable_two_factor:
                st.write("Autenticación de Dos Factores habilitada.")
            else:
                st.write("Autenticación de Dos Factores deshabilitada.")

            st.write("Ajustes relacionados con la seguridad de la aplicación.")

        elif config_choice == "Integraciones":
            st.subheader("Integraciones con APIs")
            st.markdown("### Gestionar Conexiones con Servicios Externos")

            # Mostrar conexiones actuales
            if st.session_state.api_connections:
                st.markdown("#### Conexiones Actuales")
                connections_data = []
                for api_name, api_info in st.session_state.api_connections.items():
                    connections_data.append({
                        "Nombre de la API": api_name,
                        "Información": api_info
                    })
                df_connections = pd.DataFrame(connections_data)
                st.dataframe(df_connections)

                # Botones para eliminar conexiones
                for api_name in list(st.session_state.api_connections.keys()):
                    if st.button(f"Eliminar {api_name}", key=f"delete_{api_name}"):
                        del st.session_state.api_connections[api_name]
                        st.success(f"Conexión con {api_name} eliminada exitosamente!")

            # Añadir nueva conexión
            st.markdown("#### Añadir Nueva Conexión")
            new_api_name = st.text_input("Nombre de la API")
            new_api_key = st.text_input("Clave de la API")
            if st.button("Añadir Conexión"):
                if new_api_name and new_api_key:
                    st.session_state.api_connections[new_api_name] = new_api_key
                    st.success(f"Conexión con {new_api_name} añadida exitosamente!")
                else:
                    st.error("Por favor, completa todos los campos.")

    # Conexiones con API
    elif selected == "🔗 Conexiones con API":
        st.header("Conexiones con API")
        st.markdown("### Gestionar Integraciones con APIs Externas")

        if st.session_state.api_connections:
            st.markdown("#### Conexiones Actuales")
            connections_data = []
            for api_name, api_info in st.session_state.api_connections.items():
                connections_data.append({
                    "Nombre de la API": api_name,
                    "Clave de la API": api_info
                })
            df_connections = pd.DataFrame(connections_data)
            st.dataframe(df_connections)

            # Botones para eliminar conexiones
            for api_name in list(st.session_state.api_connections.keys()):
                if st.button(f"Eliminar {api_name}", key=f"remove_{api_name}"):
                    del st.session_state.api_connections[api_name]
                    st.success(f"Conexión con {api_name} eliminada exitosamente!")
        else:
            st.info("No hay conexiones con APIs. Ve a '⚙️ Configuración' para añadir nuevas integraciones.")

        st.markdown("### Añadir Nueva Conexión")
        with st.form("add_api_form"):
            api_name = st.text_input("Nombre de la API")
            api_key = st.text_input("Clave de la API")
            submitted = st.form_submit_button("Añadir Conexión")

            if submitted:
                if api_name and api_key:
                    st.session_state.api_connections[api_name] = api_key
                    st.success(f"Conexión con {api_name} añadida exitosamente!")
                else:
                    st.error("Por favor, completa todos los campos.")

    # Diseñador de Pases
    elif selected == "🎨 Diseñador de Pases":
        st.header("Diseñador de Pases")
        st.markdown("### Crear y Generar Pases para Wallets")

        # Paso 1: Diseño del Pase
        st.subheader("Personalizar Diseño del Pase")

        with st.expander("🔧 Personalizar Diseño"):
            # Colores
            foreground_color = st.color_picker("Color de Primer Plano", "#000000")
            background_color = st.color_picker("Color de Fondo", "#FFFFFF")
            label_color = st.color_picker("Color de Etiqueta", "#000000")

            # Campos Primarios
            st.markdown("### Campos Primarios")
            primary_field_label = st.text_input("Etiqueta del Campo Primario", "Nombre")
            primary_field_value = st.text_input("Valor del Campo Primario", "Juan Pérez")

            # Campos Secundarios
            st.markdown("### Campos Secundarios")
            num_secondary = st.number_input("Número de Campos Secundarios", min_value=0, max_value=10, value=0)
            secondary_fields = []
            for i in range(int(num_secondary)):
                st.markdown(f"**Campo Secundario {i+1}**")
                key = st.text_input(f"Clave del Campo Secundario {i+1}", f"secondary_{i+1}", key=f"sec_key_{i}")
                label = st.text_input(f"Etiqueta del Campo Secundario {i+1}", f"Etiqueta {i+1}", key=f"sec_label_{i}")
                value = st.text_input(f"Valor del Campo Secundario {i+1}", f"Valor {i+1}", key=f"sec_value_{i}")
                secondary_fields.append({"key": key, "label": label, "value": value})

            # Campos Auxiliares
            st.markdown("### Campos Auxiliares")
            num_auxiliary = st.number_input("Número de Campos Auxiliares", min_value=0, max_value=10, value=0)
            auxiliary_fields = []
            for i in range(int(num_auxiliary)):
                st.markdown(f"**Campo Auxiliar {i+1}**")
                key = st.text_input(f"Clave del Campo Auxiliar {i+1}", f"auxiliary_{i+1}", key=f"aux_key_{i}")
                label = st.text_input(f"Etiqueta del Campo Auxiliar {i+1}", f"Etiqueta {i+1}", key=f"aux_label_{i}")
                value = st.text_input(f"Valor del Campo Auxiliar {i+1}", f"Valor {i+1}", key=f"aux_value_{i}")
                auxiliary_fields.append({"key": key, "label": label, "value": value})

            # Campos en la Parte Posterior
            st.markdown("### Campos en la Parte Posterior")
            num_back = st.number_input("Número de Campos en la Parte Posterior", min_value=0, max_value=10, value=0)
            back_fields = []
            for i in range(int(num_back)):
                st.markdown(f"**Campo Posterior {i+1}**")
                key = st.text_input(f"Clave del Campo Posterior {i+1}", f"back_{i+1}", key=f"back_key_{i}")
                label = st.text_input(f"Etiqueta del Campo Posterior {i+1}", f"Etiqueta {i+1}", key=f"back_label_{i}")
                value = st.text_input(f"Valor del Campo Posterior {i+1}", f"Valor {i+1}", key=f"back_value_{i}")
                back_fields.append({"key": key, "label": label, "value": value})

            # Código de Barras
            st.markdown("### Código de Barras")
            enable_barcode = st.checkbox("Agregar Código de Barras")
            barcode = {}
            if enable_barcode:
                barcode_message = st.text_input("Mensaje del Código de Barras", "123456789")
                barcode_format = st.selectbox("Formato del Código de Barras", ["PKBarcodeFormatQR", "PKBarcodeFormatPDF417", "PKBarcodeFormatAztec"])
                barcode_encoding = st.selectbox("Codificación del Código de Barras", ["iso-8859-1", "utf-8", "utf-16"])
                barcode = {
                    "enable": True,
                    "message": barcode_message,
                    "format": barcode_format,
                    "encoding": barcode_encoding
                }
            else:
                barcode = {"enable": False}

            # Diseño General
            design = {
                "foreground_color": foreground_color,
                "background_color": background_color,
                "label_color": label_color,
                "primary_field_label": primary_field_label,
                "secondary_fields": secondary_fields,
                "auxiliary_fields": auxiliary_fields,
                "back_fields": back_fields,
                "barcode": barcode,
                "text_modules": []  # Puedes extender esto según tus necesidades
            }

        # Paso 2: Ingresar Información del Pase
        st.subheader("Información del Pase")

        with st.form("pass_form"):
            name = st.text_input("Nombre", value=primary_field_value if 'primary_field_value' in locals() else "")
            description = st.text_area("Descripción", value="Descripción detallada del pase.")
            serial_number = st.text_input("Número de Serie", value="123456")
            # Agrega más campos según el tipo de pase

            # Subir imágenes
            st.markdown("### Imágenes del Pase")
            logo = st.file_uploader("Subir Logo", type=["png", "jpg"], key="logo")
            icon = st.file_uploader("Subir Ícono", type=["png", "jpg"], key="icon")
            hero_image = st.file_uploader("Subir Imagen Principal (solo para Google Wallet)", type=["png", "jpg"], key="hero_image")

            # Botón de Generar Pase
            submitted = st.form_submit_button("Generar Pase")

        # Botón de Generar Vista Previa (fuera del formulario)
        st.markdown("### Vista Previa del Pase")
        if st.button("Generar Vista Previa"):
            if logo and icon:
                try:
                    images = {}
                    images["logo.png"] = logo
                    images["icon.png"] = icon
                    if hero_image and selected == "🎨 Diseñador de Pases":
                        images["hero_image.png"] = hero_image

                    front, back = create_preview(design, {"name": name}, images)

                    # Crear marcos de teléfono para el frente y el reverso
                    front_frame = create_phone_frame(front)
                    back_frame = create_phone_frame(back)

                    # Mostrar las vistas previas lado a lado
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### Frontal del Pase")
                        st.image(front_frame, use_column_width=True)

                    with col2:
                        st.markdown("#### Posterior del Pase")
                        st.image(back_frame, use_column_width=True)
                except Exception as e:
                    st.error(f"Error al generar la vista previa: {e}")
            else:
                st.warning("Por favor, sube al menos el Logo y el Ícono para generar la vista previa.")

        # Manejo de la generación del pase después de enviar el formulario
        if submitted:
            data = {
                "name": name,
                "description": description,
                "serial_number": serial_number,
                # Agrega más datos según los campos
            }

            images = {}
            if logo:
                images["logo.png"] = logo
            if icon:
                images["icon.png"] = icon
            if hero_image and selected == "🎨 Diseñador de Pases":
                images["hero_image.png"] = hero_image

            # Seleccionar Wallet
            selected_wallet = st.selectbox("Seleccionar Wallet", ["Apple Wallet", "Google Wallet"])

            if selected_wallet == "Apple Wallet":
                try:
                    pass_path = create_apple_pass("Loyalty Card", data, images, design)
                    st.success("Pase de Apple Wallet generado exitosamente.")
                    with open(pass_path, "rb") as f:
                        st.download_button(
                            label="Descargar Pase (.json)",
                            data=f,
                            file_name=os.path.basename(pass_path),
                            mime="application/json"
                        )
                    # En una implementación real, deberías generar y descargar el archivo .pkpass
                except Exception as e:
                    st.error(f"Error al generar el pase de Apple Wallet: {e}")
            elif selected_wallet == "Google Wallet":
                try:
                    save_url = create_google_pass("Loyalty Card", data, images, design)
                    st.success("Enlace para Google Wallet generado exitosamente.")
                    st.markdown(f"[Guardar en Google Wallet]({save_url})")
                except Exception as e:
                    st.error(f"Error al generar el pase de Google Wallet: {e}")

    # Soporte al Cliente
    elif selected == "🛠️ Soporte":
        st.header("Soporte al Cliente")
        st.markdown("### Gestionar Tickets de Soporte")

        with st.form("support_form"):
            user_email = st.selectbox("Selecciona el Usuario", st.session_state.users['email'].tolist())
            issue = st.text_area("Descripción del Problema")
            submitted = st.form_submit_button("Crear Ticket")

        if submitted:
            if issue:
                new_ticket_id = len(st.session_state.support_tickets) + 1
                st.session_state.support_tickets.append({
                    "ticket_id": new_ticket_id,
                    "user_email": user_email,
                    "issue": issue,
                    "status": "Abierto",
                    "date": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                st.success(f"Ticket #{new_ticket_id} creado exitosamente!")
            else:
                st.error("Por favor, describe el problema.")

        # Mostrar tickets existentes
        if st.session_state.support_tickets:
            st.markdown("### Tickets de Soporte Existentes")
            tickets_df = pd.DataFrame(st.session_state.support_tickets)
            st.dataframe(tickets_df)

            # Botones para actualizar estado
            for ticket in st.session_state.support_tickets:
                with st.expander(f"Ticket #{ticket['ticket_id']} - {ticket['status']}"):
                    st.write(f"**Usuario:** {ticket['user_email']}")
                    st.write(f"**Descripción:** {ticket['issue']}")
                    st.write(f"**Fecha:** {ticket['date']}")

                    # Botones para actualizar estado
                    col1, col2 = st.columns(2)
                    with col1:
                        if ticket['status'] == "Abierto":
                            if st.button(f"Marcar como En Progreso", key=f"progress_{ticket['ticket_id']}"):
                                ticket['status'] = "En Progreso"
                                st.success(f"Ticket #{ticket['ticket_id']} marcado como En Progreso.")
                    with col2:
                        if ticket['status'] != "Cerrado":
                            if st.button(f"Cerrar Ticket", key=f"close_{ticket['ticket_id']}"):
                                ticket['status'] = "Cerrado"
                                st.success(f"Ticket #{ticket['ticket_id']} cerrado exitosamente.")

    # Reportes Personalizados
    elif selected == "📑 Reportes":
        st.header("Reportes Personalizados")
        st.markdown("### Generar y Descargar Reportes de la Aplicación")

        create_report()

    # A/B Testing
    elif selected == "🔬 A/B Testing":
        st.header("A/B Testing de Campañas")
        st.markdown("### Crear y Gestionar Pruebas A/B para Campañas")

        with st.form("ab_testing_form"):
            campaign = st.selectbox("Selecciona la Campaña", list(st.session_state.campaigns.keys()))
            variant = st.selectbox("Selecciona la Variante", ["A", "B", "C"])
            description = st.text_area("Descripción de la Variante")
            submitted = st.form_submit_button("Crear Variante")

        if submitted:
            if campaign and variant and description:
                new_test_id = len(st.session_state.ab_testing['tests']) + 1
                st.session_state.ab_testing['tests'].append({
                    "test_id": new_test_id,
                    "campaign": campaign,
                    "variant": variant,
                    "description": description,
                    "metrics": {"open_rate": 0.0, "click_rate": 0.0}
                })
                st.success(f"Variante '{variant}' para la campaña '{campaign}' creada exitosamente!")
            else:
                st.error("Por favor, completa todos los campos.")

        # Mostrar pruebas existentes
        if st.session_state.ab_testing['tests']:
            st.markdown("### Pruebas A/B Existentes")
            ab_tests_data = []
            for test in st.session_state.ab_testing['tests']:
                ab_tests_data.append({
                    "ID": test['test_id'],
                    "Campaña": test['campaign'],
                    "Variante": test['variant'],
                    "Descripción": test['description'],
                    "Tasa de Apertura (%)": test['metrics']['open_rate'] * 100,
                    "Tasa de Clics (%)": test['metrics']['click_rate'] * 100
                })
            df_ab_tests = pd.DataFrame(ab_tests_data)
            st.dataframe(df_ab_tests)

            # Botones para actualizar métricas
            for test in st.session_state.ab_testing['tests']:
                with st.expander(f"Prueba #{test['test_id']} - Variante {test['variant']}"):
                    st.write(f"**Campaña:** {test['campaign']}")
                    st.write(f"**Descripción:** {test['description']}")
                    st.write(f"**Tasa de Apertura:** {test['metrics']['open_rate']*100}%")
                    st.write(f"**Tasa de Clics:** {test['metrics']['click_rate']*100}%")

                    # Simular actualización de métricas
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Actualizar Tasa de Apertura", key=f"update_open_{test['test_id']}"):
                            # Simulación: incrementar tasa de apertura
                            test['metrics']['open_rate'] += 0.05
                            if test['metrics']['open_rate'] > 1.0:
                                test['metrics']['open_rate'] = 1.0
                            st.success(f"Tasa de apertura actualizada a {test['metrics']['open_rate']*100}%")
                    with col2:
                        if st.button(f"Actualizar Tasa de Clics", key=f"update_click_{test['test_id']}"):
                            # Simulación: incrementar tasa de clics
                            test['metrics']['click_rate'] += 0.05
                            if test['metrics']['click_rate'] > 1.0:
                                test['metrics']['click_rate'] = 1.0
                            st.success(f"Tasa de clics actualizada a {test['metrics']['click_rate']*100}%")
        else:
            st.write("No hay pruebas A/B creadas.")

    # Analítica
    elif selected == "📈 Analítica":
        st.header("Analítica")
        st.markdown("### Análisis Completo de la Aplicación")

        generar_graficos()

        st.markdown("### Tablas de Datos Detalladas")

        # Análisis de Usuarios
        st.subheader("Usuarios")
        # Filtro de búsqueda en usuarios
        search_user = st.text_input("Buscar Usuario por Nombre o Email")
        if search_user:
            filtered_users = st.session_state.users[
                st.session_state.users['name'].str.contains(search_user, case=False, na=False) |
                st.session_state.users['email'].str.contains(search_user, case=False, na=False)
            ]
        else:
            filtered_users = st.session_state.users

        st.markdown("#### Lista de Usuarios")
        users_display = filtered_users.copy()
        # Expandir la columna de wallets y interacciones para mostrarlas como listas o JSON
        users_display['wallets'] = users_display['wallets'].apply(json.dumps)
        users_display['interactions'] = users_display['interactions'].apply(json.dumps)
        st.dataframe(users_display[['name', 'email', 'age', 'location', 'points', 'wallet_downloaded', 'wallet_installed', 'wallet_used', 'wallets', 'interactions']])

        # Análisis de Segmentos
        st.subheader("Segmentos")
        # Filtro de búsqueda en segmentos
        search_segment = st.text_input("Buscar Segmento por Nombre", key="search_segment_analitica")
        if search_segment:
            filtered_segments = {k: v for k, v in st.session_state.segments.items() if search_segment.lower() in k.lower()}
        else:
            filtered_segments = st.session_state.segments

        if filtered_segments:
            st.markdown("#### Tabla de Segmentos")
            segment_summary = []
            for seg_name, users in filtered_segments.items():
                segment_summary.append({
                    "Segmento": seg_name,
                    "Cantidad de Usuarios": len(users)
                })
            df_segments = pd.DataFrame(segment_summary)
            st.dataframe(df_segments)

            st.markdown("#### Detalle de Usuarios por Segmento")
            for seg_name, users in filtered_segments.items():
                st.markdown(f"##### Segmento: {seg_name} ({len(users)} usuarios)")
                users_df = pd.DataFrame(users)
                st.table(users_df[['name', 'email', 'age', 'location', 'points']])
        else:
            st.write("No se encontraron segmentos que coincidan con la búsqueda.")

        # Análisis de Campañas
        st.subheader("Campañas")
        if st.session_state.campaigns:
            # Filtro de búsqueda en campañas
            search_campaign = st.text_input("Buscar Campaña por Nombre", key="search_campaign_analitica")
            if search_campaign:
                filtered_campaigns = {k: v for k, v in st.session_state.campaigns.items() if search_campaign.lower() in k.lower()}
            else:
                filtered_campaigns = st.session_state.campaigns

            if filtered_campaigns:
                df_campaigns = pd.DataFrame(filtered_campaigns).T
                df_campaigns.reset_index(inplace=True)
                df_campaigns.rename(columns={'index': 'Nombre de la Campaña'}, inplace=True)
                st.markdown("#### Lista de Campañas")
                st.dataframe(df_campaigns)
            else:
                st.write("No se encontraron campañas que coincidan con la búsqueda.")
        else:
            st.write("No hay campañas creadas.")

        # Análisis de Notificaciones Push
        st.subheader("Notificaciones Push")
        if st.session_state.push_notifications:
            # Filtro de búsqueda en notificaciones
            search_notification = st.text_input("Buscar Notificación por Título", key="search_notification_analitica")
            if search_notification:
                filtered_notifications = [notif for notif in st.session_state.push_notifications 
                                          if search_notification.lower() in notif['notification']['title'].lower()]
            else:
                filtered_notifications = st.session_state.push_notifications

            if filtered_notifications:
                notif_data = []
                for notif in filtered_notifications:
                    notif_entry = {
                        "Título": notif['notification']['title'],
                        "Mensaje": notif['notification']['message'],
                        "Campañas": ", ".join(notif['notification']['campaigns']),
                        "Usuarios Destinatarios": len(notif['users']),
                        "Fecha de Envío": notif.get('send_date', "2024-11-14")  # Añadir fecha de envío si está disponible
                    }
                    notif_data.append(notif_entry)
                df_notifs = pd.DataFrame(notif_data)
                st.markdown("#### Lista de Notificaciones Push")
                st.dataframe(df_notifs)
            else:
                st.write("No se encontraron notificaciones que coincidan con la búsqueda.")
        else:
            st.write("No se han enviado notificaciones push.")

        # Análisis de Wallets
        st.subheader("Wallets")
        wallets_data = st.session_state.users[['wallet_downloaded', 'wallet_installed', 'wallet_used']]
        st.write("**Wallets Descargadas y Instaladas:**")
        st.dataframe(wallets_data)

        st.write("**Uso de Wallets (Transacciones):**")
        st.dataframe(st.session_state.users[['name', 'wallet_used']])

        # Análisis de Fidelización
        st.subheader("Fidelización")
        st.markdown("### Puntos de Fidelización")
        st.write("**Distribución de Puntos por Usuario:**")
        st.dataframe(st.session_state.users[['name', 'points']])

        st.write("**Historial de Recompensas:**")
        if st.session_state.loyalty_program['rewards']:
            rewards_df = pd.DataFrame(st.session_state.loyalty_program['rewards'])
            st.dataframe(rewards_df)
        else:
            st.write("No hay recompensas asignadas.")

        st.write("**Historial de Redenciones:**")
        if st.session_state.loyalty_program['redemptions']:
            redemptions_df = pd.DataFrame(st.session_state.loyalty_program['redemptions'])
            st.dataframe(redemptions_df)
        else:
            st.write("No hay redenciones registradas.")

    # Buscar Wallet
    elif selected == "🔍 Buscar Wallet":
        st.header("Buscar Wallet")
        st.markdown("### Buscar una Wallet y Ver Usuarios Asociados")

        # Obtener todas las wallets únicas
        wallet_options = st.session_state.users['wallets'].explode().dropna().apply(lambda x: x['name'] if x else None).unique().tolist()
        wallet_options = [wallet for wallet in wallet_options if wallet]  # Eliminar None

        selected_wallet = st.selectbox("Selecciona una Wallet", wallet_options)

        if selected_wallet:
            # Filtrar usuarios que tienen la wallet seleccionada
            def user_has_wallet(user_wallets, wallet_name):
                return any(wallet['name'] == wallet_name for wallet in user_wallets)

            filtered_users = st.session_state.users[st.session_state.users['wallets'].apply(lambda x: user_has_wallet(x, selected_wallet))]

            if not filtered_users.empty:
                st.markdown(f"### Usuarios que Tienen {selected_wallet}")
                user_emails = filtered_users['email'].tolist()
                selected_user_email = st.selectbox("Selecciona un Usuario", user_emails)

                if selected_user_email:
                    selected_user = st.session_state.users[st.session_state.users['email'] == selected_user_email].iloc[0]

                    st.markdown(f"#### Detalles de {selected_user['name']}")

                    # Mostrar detalles del usuario en una tabla
                    user_details = {
                        "Email": selected_user['email'],
                        "Edad": selected_user['age'],
                        "Ubicación": selected_user['location'],
                        "Puntos": selected_user['points']
                    }
                    st.table(pd.DataFrame([user_details]))

                    # Detalles de Wallets en una tabla
                    st.markdown("##### Wallets Asociadas")
                    if selected_user['wallets']:
                        wallets_df = pd.DataFrame(selected_user['wallets'])
                        st.table(wallets_df)
                    else:
                        st.write("No hay wallets asociadas.")

                    # Interacciones en una tabla
                    st.markdown("##### Interacciones")
                    if selected_user['interactions']:
                        interactions_df = pd.DataFrame(selected_user['interactions'])
                        st.table(interactions_df)
                    else:
                        st.write("No hay interacciones registradas.")

                    # Gráfico de interacciones
                    if selected_user['interactions']:
                        df_trans = pd.DataFrame(selected_user['interactions'])
                        df_trans['date'] = pd.to_datetime(df_trans['date'])
                        df_trans.sort_values('date', inplace=True)
                        df_trans['cumulative_points'] = selected_user['points'] - df_trans['amount'].cumsum()
                        fig_trans = px.bar(df_trans, x='date', y='amount', color='action',
                                           title='Interacciones Detalladas',
                                           labels={'date': 'Fecha', 'amount': 'Monto', 'action': 'Acción'},
                                           barmode='group')
                        st.plotly_chart(fig_trans, use_container_width=True)
                    else:
                        st.write("No hay datos para mostrar interacciones.")
            else:
                st.write(f"No se encontraron usuarios con la wallet {selected_wallet}.")
        else:
            st.write("Por favor, selecciona una wallet para buscar.")

if __name__ == "__main__":
    main()
