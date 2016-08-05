# scanner-module
Penetration testing agent and reporting

## Fitur
1. Menjalankan tool penetration testing
2. Memberikan laporan hasil penetration testing yang sudah dirangkum

## Batasan
1. Sementara hanya mendukung penggunaan tools w3af

## Langkah-langkah instalasi (disarankan menggunakan OS Linux):
1. Install Python dan pip (disarankan)
2. Install Python Tornado dan docker-py
3. Install Docker
4. Install w3af
4. Pull image andresriancho/w3af-api dari Docker Hub
5. Kloning Repositori ini pada direktori server
6. Aplikasi siap digunakan, selanjutnya adalah langkah-langkah konfigurasi


## Langkah-langkah konfigurasi:
1. Atur alamat IP untuk tools w3af pada variabel agentList file agentRunner.py
2. Atur direktori tempat w3af terinstall pada variabel parent_dir file scanner.py
3. Atur alamat POST untuk memberikan hasil kepada Penetration Testing Dashboard pada variabel postUrl dalam class ResultRetriever fungsi run file scanner.py
4. Jalankan aplikasi dengan menggunakan perintah python webservice

**Catatan: secara default aplikasi akan berjalan pada port 8000**

**Langkah-langkah konfigurasi aplikasi akan diperbarui pada repositori ini jika terjadi perubahan terhadap aplikasi**

**Salam**
