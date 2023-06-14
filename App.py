import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import configparser

st.image('logo.png', use_column_width=1)
st.title("Calcul des heures des Radiologues")
st.sidebar.subheader("Authentification :")

def authentication():
    config = configparser.ConfigParser()
    config.read('cred_art.ini')
    mdp = config.get('Credentials', 'mdp_rhm')

    password = st.sidebar.text_input("Mot de passe :", type="password")
    if password == mdp:
        return True
    else:
        return False

def main():
    if authentication():
        st.sidebar.markdown("<p style='color:red'>Application sécurisée</p>", unsafe_allow_html=True)
        st.write("")
        pages= ['🏥 Accueil', '🚀 Chargement des données', '📈 Visualisation', '🧾Horaires des Radiologues - du 26 au 25 comptabilité']
        st.sidebar.subheader("Choisissez votre page : ")
        page=st.sidebar.radio("",pages)
        st.sidebar.subheader("")
        st.sidebar.subheader("")

        def calculate_duration(row):
            date_format = '%d/%m/%Y %H:%M:%S'
            start_date = datetime.strptime(row['Date_début'], date_format)
            end_date = datetime.strptime(row['Date_fin'], date_format)
            duration = end_date - start_date
            duration_in_seconds = duration.total_seconds()
            duration_in_hours = duration_in_seconds / 3600
            return duration_in_hours

        def download_excel(data):
            excel_file = "data.xlsx"
            data.to_excel(excel_file, index=False, header=True)
            with open(excel_file, "rb") as f:
                excel_data = f.read()
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{excel_file}">Télécharger Excel</a>'
            return href

        if page == pages[0]:
            #st.title("Calcul des heures des ART")
            st.write("Cette application vous permettra d'obtenir les heures de travail des Radiologues\n",
                    "une fois les données du planning chargée. Vous pouvez les obtenir en suivant le chemin suivant:\n",
                    "'C:\\Users\\username\\Imadis Téléradiologie\\INTRANET - IMADIS\\QUALITE\\7- RHM\\15 - DMA\\GitHub\\data'\n",
                    "Ensuite sélectionnez BDD.xlsx puis ouvrir.\n")
            #st.image("planning.png")
            
        st.sidebar.header("Données :")
        excel_file = st.sidebar.file_uploader("Charger un fichier Excel (dates les plus anciennes)", type=["xlsx", "xls"])

        if excel_file is not None: 
            # Charger le fichier Excel dans un DataFrame pandas
            df = pd.read_excel(excel_file)
            df = df[df['Date'] > '2022-12-31']
            df = df[(df['Source'] == 'PDS') | (df['Source'] == 'CDS')]
        else:
            st.write("Charger votre fichier excel pour pouvoir commencer.")  

        if page == pages[1]:
            #st.title("RH ART")
            st.header("Données :")
            st.write("Les données vont du",df['Date'].iloc[0], "au",df['Date'].iloc[-1], ".")    
            
            if st.checkbox("Afficher les données brutes :", False):
                st.subheader("Visualisation du jeu de données : ")
                st. write("Nombre de lignes et nombre de colonne :", df.shape)
                st.dataframe(df)
                st.write(df.dtypes)
            st.sidebar.image('logo.png')
            
        if page == pages[2]:
            st.header("Horaires des Radiologues")
            st.sidebar.image('logo.png')
            mois={"janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, 
                "août":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12}
            mois_select=st.selectbox("Choisissez un mois :", list(mois.keys()))
            mois_int = mois[mois_select]
            
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            mois_filtre = mois_int 
            df_filtre = df[df['Date'].dt.month == mois_filtre]
            
            if not df_filtre.empty:
                st.subheader(f"Durée totale réalisée par Radiologue pour le mois de {mois_select}")
                couleurs_sites = {"St etienne": '#38E446', "Lyon": '#0F095F', "Bordeaux":'#A62A2A', "Rennes":'#E5EA18', 
                                "Marseille": '#33F0FF', "Dijon":'#D7820B', "Clermont":"#99249F", "Brest":'#474C4C'}
                grouped_data = df_filtre.groupby(['Nom_Prenom', 'Site'])['Durée'].sum().reset_index()
                fig1=plt.figure(figsize=(20, 12))
                ax = sns.barplot(x='Nom_Prenom', y='Durée', 
                                 hue='Site', data=grouped_data, 
                                 palette=couleurs_sites, ci=None, width=0.5)
                plt.style.use('seaborn-whitegrid')
                sns.despine()
                for container in ax.containers:
                    ax.bar_label(container)
                plt.grid(True, color='lightgray')
                plt.title(f"Durée totale réalisée par Radiologue pour le mois de {mois_select}.")
                for p in ax.patches:
                    width = p.get_width()
                    height = p.get_height()
                    x, y = p.get_xy()
                plt.xlabel("Nom du Radiologue")
                plt.ylabel('Durée totale')
                plt.xticks(rotation=70, ha='right',)
                plt.legend(loc="best")
                st.pyplot(fig1)
                
                st.subheader(f"Durée cumulée réalisée par Radiologue pour le mois de {mois_select}")
                grouped_data['Durée'] = grouped_data.groupby(['Nom_Prenom'])['Durée'].cumsum()
                st.dataframe(grouped_data)
                st.markdown(download_excel(grouped_data), unsafe_allow_html=True)
                        
                st.subheader(f"Total des vacations réalisées par Radiologue pour le mois de {mois_select}")
                site_sel=st.multiselect("Site:", couleurs_sites, default=couleurs_sites)
                grouped_data2 = df_filtre.groupby(['Nom_Prenom', 'Site', 'Date'])['Durée'].sum().reset_index()
                grouped_data_filtr=grouped_data2[grouped_data2['Site'].isin (site_sel)]
                grouped_data_filtr=grouped_data_filtr.sort_values(by='Date', ascending=True)
                st.dataframe(grouped_data_filtr)
                st.markdown(download_excel(grouped_data_filtr), unsafe_allow_html=True)

        if page == pages[3]:
            st.header("Horaires des Radiologue - du 26 au 25 comptabilité")
            st.sidebar.image('logo.png')
            mois={"janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, 
                "août":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12}
            mois_select=st.selectbox("Choisissez un mois :", list(mois.keys()))
            mois_int = mois[mois_select]

            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            #mois_filtre = mois_int 
            #df_filtre = df[df['Date'].dt.month == mois_filtre]
            #             
            # Obtenir la date actuelle
            date_actuelle = datetime.now()

            # Déterminer le mois précédent
            mois_precedent = date_actuelle.month - 1 if date_actuelle.month > 1 else 12

            # Obtenir l'année correspondante pour le mois précédent
            annee_precedente = date_actuelle.year if date_actuelle.month > 1 else date_actuelle.year - 1

            # Déterminer la date de début (26 du mois précédent)
            date_debut = datetime(annee_precedente, mois_precedent, 26)

            # Déterminer la date de fin (25 du mois sélectionné)
            date_fin = datetime(date_actuelle.year, mois_int, 25)
            df_filtre = df[(df['Date'] >= date_debut) & (df['Date'] <= date_fin)]
            
            if not df_filtre.empty:
                st.subheader(f"Durée totale réalisée par Radiologue du {date_debut.day}/{date_debut.month} au {date_fin.day}/{date_fin.month}")
                couleurs_sites = {"St etienne": '#38E446', "Lyon": '#0F095F', "Bordeaux":'#A62A2A', "Rennes":'#E5EA18', 
                                "Marseille": '#33F0FF', "Dijon":'#D7820B', "Clermont":"#99249F", "Brest":'#474C4C'}
                grouped_data = df_filtre.groupby(['Nom_Prenom', 'Site'])['Durée'].sum().reset_index()
                fig2=plt.figure(figsize=(20, 12))
                ax = sns.barplot(x='Nom_Prenom', y='Durée', 
                                 hue='Site', data=grouped_data, 
                                 palette=couleurs_sites, ci=None, width=0.5)
                plt.style.use('seaborn-whitegrid')
                sns.despine()
                for container in ax.containers:
                    ax.bar_label(container)
                plt.grid(True, color='lightgray')
                plt.title(f"Durée totale réalisée par Radiologue pour le mois de {mois_select}.")
                for p in ax.patches:
                    width = p.get_width()
                    height = p.get_height()
                    x, y = p.get_xy()
                plt.xlabel("Nom du Radiologue")
                plt.ylabel('Durée totale')
                plt.xticks(rotation=70, ha='right',)
                plt.legend(loc="best")
                st.pyplot(fig2)
                
                st.subheader(f"Durée cumulée réalisée par Radiologue pour le mois de {mois_select}")
                grouped_data['Durée'] = grouped_data.groupby(['Nom_Prenom'])['Durée'].cumsum()
                st.dataframe(grouped_data)
                st.markdown(download_excel(grouped_data), unsafe_allow_html=True)
                        
                st.subheader(f"Total des vacations réalisées par Radiologue pour le mois de {mois_select}")
                site_sel=st.multiselect("Site:", couleurs_sites, default=couleurs_sites)
                grouped_data2 = df_filtre.groupby(['Nom_Prenom', 'Site', 'Date'])['Durée'].sum().reset_index()
                grouped_data_filtr=grouped_data2[grouped_data2['Site'].isin (site_sel)]
                grouped_data_filtr=grouped_data_filtr.sort_values(by='Date', ascending=True)
                st.dataframe(grouped_data_filtr)
                st.markdown(download_excel(grouped_data_filtr), unsafe_allow_html=True)

            else:
                st.write(f"Aucune donnée disponible pour le mois {mois_select}.")
        
        
    else:
        st.error("Mot de passe incorrect")
 
if __name__ == '__main__':
    main()


