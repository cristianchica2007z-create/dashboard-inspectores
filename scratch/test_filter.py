import requests

TOKEN = "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"
REPO = "cristianchica2007z-create/dashboard-inspectores"

def check_api():
    try:
        # 1. Get Config
        r = requests.get(f"http://localhost:8000/config?repo={REPO}&token={TOKEN}")
        config = r.json()
        print("Config API Response:", config)
        
        fechas = config.get('fechas', [])
        if not fechas:
            print("No hay fechas disponibles.")
            return
            
        test_fecha = fechas[0]
        print(f"\nUsando fecha: {test_fecha}")

        # 2. Get Summary without filter
        r_all = requests.get(f"http://localhost:8000/summary?repo={REPO}&token={TOKEN}&fecha={test_fecha}")
        all_data = r_all.json()
        print(f"Total inspecciones (SIN FILTRO): {all_data.get('total_inspecciones')}")
        
        # 3. Get Summary with each supervisor
        sups = config.get('supervisores', [])
        total_filtered = 0
        for sup in sups:
            if sup == 'TODOS': continue
            r_sup = requests.get(f"http://localhost:8000/summary?repo={REPO}&token={TOKEN}&fecha={test_fecha}&supervisor={sup}")
            sup_data = r_sup.json()
            count = sup_data.get('total_inspecciones', 0)
            print(f"  - {sup}: {count} inspecciones")
            total_filtered += count
            
        print(f"\nSuma de inspecciones filtradas: {total_filtered}")
        
        # 4. Check inspections_agregada too
        print("\nVerificando /inspections_agregada:")
        r_insp = requests.get(f"http://localhost:8000/inspections_agregada?repo={REPO}&token={TOKEN}&fecha={test_fecha}")
        if r_insp.status_code != 200:
            print(f"Error {r_insp.status_code}: {r_insp.text}")
        else:
            insp_all = r_insp.json()
            print(f"Total inspectores (SIN FILTRO): {len(insp_all)}")
        
        if len(sups) > 1:
            test_sup = sups[1]
            print(f"\nProbando /inspections_agregada con {test_sup}:")
            r_insp_filt = requests.get(f"http://localhost:8000/inspections_agregada?repo={REPO}&token={TOKEN}&fecha={test_fecha}&supervisor={test_sup}")
            if r_insp_filt.status_code != 200:
                print(f"Error {r_insp_filt.status_code} (Filtrado): {r_insp_filt.text}")
            else:
                insp_filt = r_insp_filt.json()
                print(f"Total inspectores (Filtrado): {len(insp_filt)}")

        if total_filtered == all_data.get('total_inspecciones'):
            print("\n>>> EL FILTRO FUNCIONA CORRECTAMENTE EN EL BACKEND <<<")
        else:
            print("\n>>> HAY UNA DISCREPANCIA EN EL FILTRO <<<")

    except Exception as e:
        print("Error conectando a la API:", e)

if __name__ == "__main__":
    check_api()
