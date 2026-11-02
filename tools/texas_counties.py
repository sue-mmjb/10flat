"""The 254 counties of Texas, for the county suggestions on /start and the check in api/intake.js."""

COUNTIES = """Anderson Andrews Angelina Aransas Archer Armstrong Atascosa Austin Bailey Bandera Bastrop Baylor Bee Bell Bexar
Blanco Borden Bosque Bowie Brazoria Brazos Brewster Briscoe Brooks Brown Burleson Burnet Caldwell Calhoun Callahan Cameron
Camp Carson Cass Castro Chambers Cherokee Childress Clay Cochran Coke Coleman Collin Collingsworth Colorado Comal Comanche
Concho Cooke Coryell Cottle Crane Crockett Crosby Culberson Dallam Dallas Dawson Deaf_Smith Delta Denton DeWitt Dickens
Dimmit Donley Duval Eastland Ector Edwards El_Paso Ellis Erath Falls Fannin Fayette Fisher Floyd Foard Fort_Bend Franklin
Freestone Frio Gaines Galveston Garza Gillespie Glasscock Goliad Gonzales Gray Grayson Gregg Grimes Guadalupe Hale Hall
Hamilton Hansford Hardeman Hardin Harris Harrison Hartley Haskell Hays Hemphill Henderson Hidalgo Hill Hockley Hood Hopkins
Houston Howard Hudspeth Hunt Hutchinson Irion Jack Jackson Jasper Jeff_Davis Jefferson Jim_Hogg Jim_Wells Johnson Jones
Karnes Kaufman Kendall Kenedy Kent Kerr Kimble King Kinney Kleberg Knox La_Salle Lamar Lamb Lampasas Lavaca Lee Leon Liberty
Limestone Lipscomb Live_Oak Llano Loving Lubbock Lynn Madison Marion Martin Mason Matagorda Maverick McCulloch McLennan
McMullen Medina Menard Midland Milam Mills Mitchell Montague Montgomery Moore Morris Motley Nacogdoches Navarro Newton Nolan
Nueces Ochiltree Oldham Orange Palo_Pinto Panola Parker Parmer Pecos Polk Potter Presidio Rains Randall Reagan Real Red_River
Reeves Refugio Roberts Robertson Rockwall Runnels Rusk Sabine San_Augustine San_Jacinto San_Patricio San_Saba Schleicher
Scurry Shackelford Shelby Sherman Smith Somervell Starr Stephens Sterling Stonewall Sutton Swisher Tarrant Taylor Terrell
Terry Throckmorton Titus Tom_Green Travis Trinity Tyler Upshur Upton Uvalde Val_Verde Van_Zandt Victoria Walker Waller Ward
Washington Webb Wharton Wheeler Wichita Wilbarger Willacy Williamson Wilson Winkler Wise Wood Yoakum Young Zapata Zavala""".split()
COUNTIES = [c.replace("_", " ") for c in COUNTIES]

assert len(COUNTIES) == 254, len(COUNTIES)
assert len(set(COUNTIES)) == 254
