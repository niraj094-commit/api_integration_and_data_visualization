import requests
import matplotlib.pyplot as matplt
import pandas as pd
import seaborn as sea
import os

# To make sure this file Runs in the current folder on double clicking this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

sea.set_style("dark")
matplt.rcParams["figure.figsize"] = (20,20)

## gonna tweak these later! (For Decent Look!)

matplt.rcParams["font.size"] = 16
matplt.rcParams["lines.linewidth"] = 3
matplt.rcParams["axes.grid"] = True



user_search_input = input("What book are you lookin'for (Default: Python): " ) 
if user_search_input is None or user_search_input == "":
    user_search_input = "Python"

PageNo = input("It could even search with Page No too! (Default is 1)\nEnter PageNo: ")

if PageNo is None or PageNo == "":
    PageNo = 1
else:
    PageNo = int(PageNo)

print("Starting the Project...")


api_Endpoint = "https://openlibrary.org/search.json"    # Search wala API endpoint

# So! Its a dict. of the parameters , we'll be sending to the API
parameters = {"q" : user_search_input,"limit" : 50,"fields" : "title,author_name,first_publish_year,subject,language,ebook_access","page" : PageNo}


       
try:
    response = requests.get(api_Endpoint , params = parameters)
    data = response.json()
    # print(data)  # For me!!
    raw_dta = data.get("docs", [])
except requests.exceptions.RequestException as e:
    print(f"Error getting data: {e}")
    raw_dta = None

if raw_dta is None:
    print("No Results Found! or Maybe some error occurred!")
    
formatted_data = pd.DataFrame(raw_dta)

# Now we'll be Formatting the Data we got from the call:

print("Formatting the Data...")

if "author_name" in formatted_data.columns:
    formatted_data["author_name"] = formatted_data["author_name"].fillna("Unknown")
    formatted_data["author_name"] = formatted_data["author_name"].apply(lambda x: x[0] if isinstance(x,list) else x)
else:
    formatted_data["author_name"] = "Unknown"


if "first_publish_year" in formatted_data.columns:
    formatted_data["first_publish_year"] = formatted_data["first_publish_year"].fillna(0).astype(int)
else:
    formatted_data["first_publish_year"] = 0


if "subject" in formatted_data.columns:
    formatted_data["subject"] = formatted_data["subject"].fillna("")
    formatted_data["subject"] = formatted_data["subject"].apply(lambda x: x[0] if isinstance(x,list) and len(x) > 0 else "Unknown")
else:
    formatted_data["subject"] = "Unknown"


if 'language' in formatted_data.columns:
    formatted_data['language'] = formatted_data['language'].fillna('')
    formatted_data['language'] = formatted_data['language'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 'Unknown')
else:
    formatted_data['language'] = 'Unknown'


if 'ebook_access' in formatted_data.columns:
    formatted_data['ebook_access'] = formatted_data['ebook_access'].fillna('no_ebook')
else:
    formatted_data['ebook_access'] = 'no_ebook'


author_counts = formatted_data["author_name"].value_counts().reset_index()
author_counts.columns = ["author","book_count"]


subject_counts = formatted_data["subject"].value_counts().reset_index()
subject_counts.columns = ["subject","book_count"]

print("Data Formatting Completed!")


## Creating Visual Now! (MatPlotLib and Seaborn)

visual = {}

print("Creating Visuals...")
# Books Published vs Year:

matplt.figure(figsize=(20,10))
year_counts = formatted_data[formatted_data["first_publish_year"] > 0] ["first_publish_year"].value_counts().sort_index()
sea.lineplot(x=year_counts.index, y=year_counts.values, marker='o')
matplt.title("Books Published vs Year")
matplt.xlabel("Year in which the book was Published")
matplt.ylabel("Number of Books")
matplt.xticks(rotation=0)  # This is not actuaaly needed but chalo koi na!
matplt.tight_layout()      # It makes elements fit nicely to the area
visual["No_of_Books_vs_Year"] = matplt.gcf()
matplt.close()


# Top 10 Authors vs Book Count:

matplt.figure(figsize=(20,10))
Top_Authors = author_counts.head(10)
sea.barplot(x="book_count", y="author", data=Top_Authors, palette = "plasma",hue = "author",legend = False)
matplt.title("Top 10 Authors vs Book Count")
matplt.xlabel("Number of Books")
matplt.ylabel("Authors")
matplt.yticks(rotation=45)
matplt.tight_layout()      # It makes elements fit nicely to the area
visual["Top_Authors"] = matplt.gcf()
matplt.close()


# Top 10 Subjects vs Book Count:

matplt.figure(figsize=(20, 10))
Top_Subjects = subject_counts.head(10)
sea.barplot(x="book_count", y="subject", data=Top_Subjects, palette="inferno",hue="subject",legend=False)
matplt.title('Top 10 Book Subjects')
matplt.xlabel("Number of Books")
matplt.ylabel("Subject")
matplt.yticks(rotation=45)
matplt.tight_layout()      # It makes elements fit nicely to the area
visual["top_subjects"] = matplt.gcf()
matplt.close()


# Ebook Availability Pie-Chart:

matplt.figure(figsize=(20, 10))
avail_counts = formatted_data["ebook_access"].value_counts()
matplt.pie(avail_counts, labels = avail_counts.index,autopct='%1.1f%%', startangle=90, colors=sea.color_palette('inferno'))
matplt.title("Ebook Availability")
visual["Ebook_Avail"] = matplt.gcf()
matplt.close()


## Ah! FInally getting to save the visuals as PNGs:

saved_PNGs = {}
for name, fig in visual.items():
    png_fn = f"results-{name}.png"
    fig.savefig(png_fn, bbox_inches='tight', dpi=300)
    saved_PNGs[name] = png_fn
print(f"Files saved successfully!: {saved_PNGs.keys()}")


## Now making a Dashboard as it is required in the project:

print("Creating Dashboard...")
fig, axes = matplt.subplots(2, 2, figsize=(20, 10))

# 1st
visual["No_of_Books_vs_Year"].canvas.draw()
img1 = visual["No_of_Books_vs_Year"]
axes[0, 0].imshow(img1.canvas.renderer.buffer_rgba())
axes[0, 0].axis("off")
axes[0, 0].set_title("Books Published by Year", pad=20)

# 2nd
visual["Top_Authors"].canvas.draw()
img2 = visual["Top_Authors"]
axes[0, 1].imshow(img2.canvas.renderer.buffer_rgba())
axes[0, 1].axis("off")
axes[0, 1].set_title("Top 10 Authors by Book Count", pad=20)

# 3rd
visual["top_subjects"].canvas.draw()
img3 = visual["top_subjects"]
axes[1, 0].imshow(img3.canvas.renderer.buffer_rgba())
axes[1, 0].axis("off")
axes[1, 0].set_title("Top 10 Book Subjects", pad=20)

# 4th
visual["Ebook_Avail"].canvas.draw()
img4 = visual["Ebook_Avail"]
axes[1, 1].imshow(img4.canvas.renderer.buffer_rgba())
axes[1, 1].axis("off")
axes[1, 1].set_title('Ebook Availability', pad=20)



matplt.suptitle("Open Library Data Dashboard", fontsize=24, y=1.02)
matplt.tight_layout()
dashboard_filename = "dashboard.png"
matplt.savefig(dashboard_filename, bbox_inches="tight", dpi=300)
matplt.close()

print("Dashboard created and saved as {dashboard_filename}!")

print("Project Completed Successfully!")
