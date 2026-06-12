import sqlite3, json, sys, re
sys.path.insert(0, '.')
from db import Database

db = Database()

# Get existing emails for deduplication
cursor = db.conn.cursor()
cursor.execute('SELECT email FROM recipients')
existing = set(e[0].lower().strip() for e in cursor.fetchall() if e[0])
print(f'Existing emails in pool: {len(existing)}')

# BSAI Boarding Schools emails
bsai_emails = [
    ('principal@academicworld.co.in', 'Academic World School', 'Chhattisgarh'),
    ('preeti.saini@academicworld.co.in', 'Academic World School', 'Chhattisgarh'),
    ('principal@allsaintscollege.org', 'All Saints College', 'Uttarakhand'),
    ('chanigupta@gmail.com', 'All Saints College', 'Uttarakhand'),
    ('head@assamvalleyschool.com', 'Assam Valley School', 'Assam'),
    ('hop@assamvalleyschool.com', 'Assam Valley School', 'Assam'),
    ('principal@barneschool.in', 'Barnes School & Junior College', 'Maharashtra'),
    ('pallavi.kasar@barnesschool.in', 'Barnes School & Junior College', 'Maharashtra'),
    ('principal@billimoriahighschool.com', 'Billimoria High School', 'Maharashtra'),
    ('admin@billimoriahighschool.com', 'Billimoria High School', 'Maharashtra'),
    ('principal@bbvpilani.edu.in', 'Birla Balika Vidyapeeth', 'Rajasthan'),
    ('renu030033@bbvpilani.edu.in', 'Birla Balika Vidyapeeth', 'Rajasthan'),
    ('principal@bisk.edu.in', 'Birla Public School Kishangarh', 'Rajasthan'),
    ('acsr@bisk.edu.in', 'Birla Public School Kishangarh', 'Rajasthan'),
    ('principal@birlaschoolpilani.edu.in', 'Birla School Pilani', 'Rajasthan'),
    ('surbhi030075@birlaschoolpilani.edu.in', 'Birla School Pilani', 'Rajasthan'),
    ('headmaster@bishopcotton.com', 'Bishop Cotton School Shimla', 'Himachal Pradesh'),
    ('smpastoral@bishopcottonshimla.com', 'Bishop Cotton School Shimla', 'Himachal Pradesh'),
    ('principal@cpsudaipur.com', 'Central Public School', 'Rajasthan'),
    ('principal.rohania@dalimss.com', 'Dalimss Sunbeam School Rohania', 'Uttar Pradesh'),
    ('associatehead@dalimss.com', 'Dalimss Sunbeam School Rohania', 'Uttar Pradesh'),
    ('ecoleglobale@gmail.com', 'Ecole Globale International Girls School', 'Uttarakhand'),
    ('afifa@ecoleglobale.com', 'Ecole Globale International Girls School', 'Uttarakhand'),
    ('principal@heritagegirlsschool.com', 'Heritage Girls School', 'Rajasthan'),
    ('nainapankaj@yahoo.com', 'Him Academy Public School', 'Himachal Pradesh'),
    ('prakritlakhanpal@himacademy.com', 'Him Academy Public School', 'Himachal Pradesh'),
    ('principal@hopetown.in', 'Hopetown Girls School', 'Uttarakhand'),
    ('jyotikharkwal240@hopetown.co.in', 'Hopetown Girls School', 'Uttarakhand'),
    ('sanjeeva.sinha@jirs.ac.in', 'Jain International Residential School', 'Karnataka'),
    ('principallks@gmail.com', 'L K Singhania Education Centre', 'Rajasthan'),
    ('sandeeplksecg@gmail.com', 'L K Singhania Education Centre', 'Rajasthan'),
    ('principal@lamartinierelucknow.org', 'La Martiniere College', 'Uttar Pradesh'),
    ('ccalamartiniere@gmail.com', 'La Martiniere College', 'Uttar Pradesh'),
    ('principal@laidlowschool.org', 'Laidlow Memorial', 'Tamil Nadu'),
    ('principal.mvaburhanpur.com', 'Macro Vision Academy', 'Madhya Pradesh'),
    ('kabirchouksey@mvaburhanpur.com', 'Macro Vision Academy', 'Madhya Pradesh'),
    ('director@mgdschooljaipur.com', 'Maharani Gayatri Devi Girls School', 'Rajasthan'),
    ('cambridge@mgdschooljaipur.com', 'Maharani Gayatri Devi Girls School', 'Rajasthan'),
    ('principal@mayocollege.com', 'Mayo College', 'Rajasthan'),
    ('principal@mcgs.ac.in', 'Mayo College Girls School', 'Rajasthan'),
    ('ysbhati@mcgs.ac.in', 'Mayo College Girls School', 'Rajasthan'),
    ('nripen.dutta@gmail.com', 'Miles Bronson Residential School', 'Assam'),
    ('henaaduttaa@gmail.com', 'Miles Bronson Residential School', 'Assam'),
    ('principal@modiworldschool.com', 'Modi World School', 'Rajasthan'),
    ('krd.dhinwa@gmail.com', 'Modi World School', 'Rajasthan'),
    ('principal@misindia.org', 'Mussorie International School', 'Uttarakhand'),
    ('viceprincipal@misindia.org', 'Mussorie International School', 'Uttarakhand'),
    ('schooldirector.pws@pathways.in', 'Pathways World School', 'Haryana'),
    ('director@pinegroveschool.com', 'Pinegrove School', 'Himachal Pradesh'),
    ('bsairep@pinegroveschool.com', 'Pinegrove School', 'Himachal Pradesh'),
    ('neerasingh_rkk@yahoo.com', 'Rajmata Krishna Kumari Girls Public School', 'Rajasthan'),
    ('exch.programrep@rkkgps.com', 'Rajmata Krishna Kumari Girls Public School', 'Rajasthan'),
    ('umesh@rishikulvidyapeeth.edu.in', 'Rishikul Vidyapeeth', 'Haryana'),
    ('nisha@rishikulvidyapeeth.edu.in', 'Rishikul Vidyapeeth', 'Haryana'),
    ('rcskriti@gmail.com', 'Roots Country School', 'Himachal Pradesh'),
    ('jagmohan.educomp@gmail.com', 'Roots Country School', 'Himachal Pradesh'),
    ('principal@sadhbhavanaschool.org', 'Sadhbhavana World School', 'Kerala'),
    ('harish@sadhbhavana.com', 'Sadhbhavana World School', 'Kerala'),
    ('headmaster@sirs.edu.in', 'Sai International Residential School', 'Orissa'),
    ('dhm@sirs.edu.in', 'Sai International Residential School', 'Orissa'),
    ('principal@sgischool.in', 'Sanjay Ghodwat International School', 'Maharashtra'),
    ('residentialprincipal@sgischool.in', 'Sanjay Ghodwat International School', 'Maharashtra'),
    ('principal@skvgwalior.org', 'Scindia Kanya Vidyalaya', 'Madhya Pradesh'),
    ('info@skvgwalior.org', 'Scindia Kanya Vidyalaya', 'Madhya Pradesh'),
    ('headmaster@selaqui.org', 'Selaqui International School', 'Uttarakhand'),
    ('pstr.srmaster@selaqui.org', 'Selaqui International School', 'Uttarakhand'),
    ('principal.babatpur@jaipuriaschools.ac.in', 'Seth M.R Jaipuria Schools Banaras', 'Uttar Pradesh'),
    ('info.babatpur@jaipuriaschools.ac.in', 'Seth M.R Jaipuria Schools Banaras', 'Uttar Pradesh'),
    ('principal.mcm@vallabhashram.in', 'Shree Vallabh Ashram MCM Kothari School', 'Gujarat'),
    ('school.mcm@vallabhashram.in', 'Shree Vallabh Ashram MCM Kothari School', 'Gujarat'),
    ('hos@ssvminstitutions.ac.in', 'SSVM Mettupalayam', 'Tamil Nadu'),
    ('arthipriyat@ssvminstitutions.ac.in', 'SSVM Mettupalayam', 'Tamil Nadu'),
    ('principal@sgconline.ac.in', 'St. Georges College', 'Uttarakhand'),
    ('bhavneshnegi7700@gmail.com', 'St. Georges College', 'Uttarakhand'),
    ('principal.bhagwanpur@sunbeamschools.com', 'Sunbeam English School Bhagwanpur', 'Uttar Pradesh'),
    ('bgnhostel@sunbeamschools,com', 'Sunbeam English School Bhagwanpur', 'Uttar Pradesh'),
    ('principal.lahartara@sunbeamschools.com', 'Sunbeam School Lahartara', 'Uttar Pradesh'),
    ('sanjeevpandey14229@gmail.com', 'Sunbeam School Lahartara', 'Uttar Pradesh'),
    ('principal.suncity@sunbeamschools.com', 'Sunbeam Suncity School', 'Uttar Pradesh'),
    ('cbhushan@sunbeamschools.co.in', 'Sunbeam Suncity School', 'Uttar Pradesh'),
    ('principal.varuna@sunbeamschools.com', 'Sunbeam Varuna School', 'Uttar Pradesh'),
    ('alok.sunbeamvaruna@gmail.com', 'Sunbeam Varuna School', 'Uttar Pradesh'),
    ('ppl@synainternational.edu.in', 'Syna International School', 'Madhya Pradesh'),
    ('raj.shukla@synainternational.edu.in', 'Syna International School', 'Madhya Pradesh'),
    ('principal@tws.edu.in', 'Taurian World School', 'Jharkhand'),
    ('boarding.head@tws.edu.in', 'Taurian World School', 'Jharkhand'),
    ('principaltheasianschool@gmail.com', 'The Asian School', 'Uttarakhand'),
    ('hortasddn@gmail.com', 'The Asian School', 'Uttarakhand'),
    ('md@thedoongirlsschool.com', 'The Doon Girls School', 'Uttarakhand'),
    ('officebsai.india@gmail.com', 'The Doon School', 'Uttarakhand'),
    ('dep@doonschool.com', 'The Doon School', 'Uttarakhand'),
    ('director@emeraldheights.edu.in', 'The Emerald Heights International School', 'Madhya Pradesh'),
    ('activities@emeraldheights.edu.in', 'The Emerald Heights International School', 'Madhya Pradesh'),
    ('principal@kasigaschool.com', 'The Kasiga School', 'Uttarakhand'),
    ('dbrien@kasigaschool.com', 'The Kasiga School', 'Uttarakhand'),
    ('headmaster@sanawar.edu.in', 'The Lawrence School Sanawar', 'Himachal Pradesh'),
    ('ranbir.randhawa@sanwar.edu.in', 'The Lawrence School Sanawar', 'Himachal Pradesh'),
    ('hm@thelawrenceschool.org', 'The Lawrence School Lovedale', 'Tamil Nadu'),
    ('principal@themannschool.com', 'The Mann School', 'Delhi'),
    ('dheeraj.kumar@themannschool.com', 'The Mann School', 'Delhi'),
    ('hmppsnabha@yahoo.com', 'The Punjab Public School Nabha', 'Punjab'),
    ('principal@rkcrajkot.in', 'The Rajkumar College', 'Gujarat'),
    ('yash@rkcrajkot.in', 'The Rajkumar College', 'Gujarat'),
    ('falguni@rkcrajkot.in', 'The Rajkumar College', 'Gujarat'),
    ('principal@royalcollege.in', 'The Royal College', 'Uttarakhand'),
    ('ronr0006@gmail.com', 'The Royal College', 'Uttarakhand'),
    ('principal@sanskaarvalley.org', 'The Sanskaar Valley School', 'Madhya Pradesh'),
    ('kamal_soni@sanskaarvalley.org', 'The Sanskaar Valley School', 'Madhya Pradesh'),
    ('principal@scindia.edu', 'The Scindia School', 'Madhya Pradesh'),
    ('MANOJM@SCINDIA.EDU', 'The Scindia School', 'Madhya Pradesh'),
    ('headmaster@tis.edu.in', 'Tulas International School', 'Uttarakhand'),
    ('swati.thapa@tis.edu.in', 'Tulas International School', 'Uttarakhand'),
    ('principal@uws.edu.in', 'Unison World School', 'Uttarakhand'),
    ('richa.mehra@uws.edu.in', 'Unison World School', 'Uttarakhand'),
    ('principal.mgm@vallabhashram.in', 'Vallabh Ashram MGM School', 'Gujarat'),
    ('ks@vallabhashram.in', 'Vallabh Ashram MGM School', 'Gujarat'),
    ('principal@vantagehall.org', 'Vantage Hall Girls Residential School', 'Uttarakhand'),
    ('smiitaa.pandey@vantagehall.org', 'Vantage Hall Girls Residential School', 'Uttarakhand'),
    ('principal@vischennai.ac.in', 'Vellore International School', 'Tamil Nadu'),
    ('academiccoordinator.caie@vischennai.ac.in', 'Vellore International School', 'Tamil Nadu'),
    ('principal@vdjs.edu.in', 'Vidya Devi Jindal School', 'Haryana'),
    ('vijaysobhani@vdjs.edu.in', 'Vidya Devi Jindal School', 'Haryana'),
    ('principal@bpspilani.edu.in', 'Vidya Niketan Birla Public School', 'Rajasthan'),
    ('anil2008@bpspilani.edu.in', 'Vidya Niketan Birla Public School', 'Rajasthan'),
    ('meera.pandey@vidyagan.in', 'Vidyagyan Leadership Academy', 'Uttar Pradesh'),
    ('ad534@vidyagan.in', 'Vidyagyan Leadership Academy', 'Uttar Pradesh'),
    ('ss640@vidyagan.in', 'Vidyagyan Leadership Academy', 'Uttar Pradesh'),
    ('Don.Augustine@vidyagan.in', 'Vidyagyan Leadership Academy', 'Uttar Pradesh'),
    ('hos@mitgurukul.com', 'Vishwashanti Gurukul World School', 'Maharashtra'),
    ('sonia.m@mitgurukul.com', 'Vishwashanti Gurukul World School', 'Maharashtra'),
    ('principal@welhamboys.org', 'Welham Boys School', 'Uttarakhand'),
    ('kritikadhyani@welhamboys.org', 'Welham Boys School', 'Uttarakhand'),
    ('principal@welhamgirls.com', 'Welham Girls School', 'Uttarakhand'),
    ('Deanpastoralcare@welhamgirls.com', 'Welham Girls School', 'Uttarakhand'),
    ('principal@woodstock.ac.in', 'Woodstock School', 'Uttarakhand'),
    ('director@ypschd.com', 'Yadavindra Public School Mohali', 'Punjab'),
    ('amitazsinghsidu@ypschd.com', 'Yadavindra Public School Mohali', 'Punjab'),
    ('headmaster@ypspatiala.in', 'Yadavindra Public School Patiala', 'Punjab'),
    ('kushalbir.kaur@ypspatiala.in', 'Yadavindra Public School Patiala', 'Punjab'),
]

# Mumbai CBSE schools from schoolsindia.net
mumbai_emails = [
    ('albarkaatschool@yahoo.com', 'Al Barkaat School', 'Mumbai'),
    ('info@avnavimumbai.com', 'AVN School Navi Mumbai', 'Mumbai'),
    ('skool.nrl.by@apj.edu', 'Army School Navi Mumbai', 'Mumbai'),
    ('armyschoolmumbai@gmail.com', 'Army School Mumbai', 'Mumbai'),
    ('principal.bbkgr@gmail.com', 'Bai Kabibai School', 'Mumbai'),
]

added = 0
skipped = 0
errors = 0
all_emails = bsai_emails + mumbai_emails

for email, name, org in all_emails:
    email_clean = email.lower().strip()
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email_clean):
        print(f'[INVALID] {email}')
        errors += 1
        continue
    if email_clean in existing:
        skipped += 1
        continue
    extra = json.dumps({'source': 'web_bsai_boarding', 'state': org, 'category': 'Boarding School'})
    ok, err = db.recipient_add('school', email, name, org, extra)
    if ok:
        added += 1
        existing.add(email_clean)
    else:
        print(f'[ERR] {email} - {err}')
        errors += 1

print(f'\n=== BSAI + Mumbai IMPORT ===')
print(f'Added: {added}')
print(f'Skipped (duplicates): {skipped}')
print(f'Errors/Invalid: {errors}')
print(f'Total processed: {len(all_emails)}')

# Show current counts
cursor.execute("SELECT sequence_id, COUNT(*) FROM recipients GROUP BY sequence_id")
for row in cursor.fetchall():
    print(f'Total {row[0]} recipients: {row[1]}')

db.conn.close()
