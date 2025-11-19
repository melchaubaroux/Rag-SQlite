# splitting by font size pdf
import pymupdf4llm

name_file="analyse exctraction"
path=r"C:\Users\melch\Desktop\manette_help_tool\manette_help_tool\rag\Scripts\ressource_documents\ManetteTools documentation_2025.pdf"

# with open(name_file,"w",encoding="utf-8") as file : 
#     file.write(pymupdf4llm.to_markdown(path))



# liste_titre=[]
# with open(name_file,"r",encoding="utf-8") as file : 
#     liste_lines=file.readlines()

#     for x in liste_lines : 
#         if '#'==x[0] : 
#             liste_titre+=[x]

        
#     with open("exctract_title","w",encoding="utf-8") as file : 
#         for x in liste_titre :

#             file.write(str(x))



path=r"C:\Users\melch\Desktop\manette_help_tool\manette_help_tool\analyse_exctraction"

def get_next_chunk (file,size,overflow="") : 

    chunk=overflow+file.read(size)
    lignes=chunk.split("\n")
    overflow=lignes[-1]

    return lignes[:-1],overflow


def process_chunk(chunk) : 
    pass

def is_title(string):
    #print("ligne : ",l)

    return  True if len(string) > 0 and string[0]=="#" else False


def calculate_indent (string) : 
    indent=0
    for x in string : 
        if x!='#' : return indent
        else : indent+=1

    return indent



arbo=[]
cursor=[]

temps=[]
compteur=0
tmp_cursor=[]
tmp_counter=0
   
with open (path,"r",encoding="utf-8") as file : 

    temp=[]

    while True :

        lignes,overflow=get_next_chunk(file,4094,"")
        if len(lignes)==0: break 

        for l in lignes : 

            if is_title(l)==True:

                # print("title : ",l)

                t= cursor[-1] if len(cursor)>0 else ""

                if calculate_indent(t)<calculate_indent(l) : 

                    cursor+=[l]
                    tmp_cursor+=[len(temp)]

                elif calculate_indent(t)==calculate_indent(l) : 

                    # print("title : ",cursor[-1])


                    arbo+=[cursor]
                    cursor=cursor[:-1]+[l]
                    temps+=[temp]
                    temp=temp[:tmp_cursor[-1]]
                    compteur+=1

                else : 
                    # print("title : ",cursor[-1])
                    arbo+=[cursor]

                    indentation_count=0
                    iterrator=iter(l)
                    first=next(iterrator)
                    while first=="#" : 
                        indentation_count+=1
                        first=next(iterrator)

                    
                    cursor=cursor[:indentation_count]+[l]
                    temps+=[temp]
                    tmp_cursor=tmp_cursor[:indentation_count]
                    temp=temp[:tmp_cursor[-1]]
                    compteur+=1

            else : 

                temp+=[l]
                tmp_counter+=1
                pass


        
        

    
    compteur+=1
    arbo+=[cursor]
    temps+=[temp]

    
print(compteur,len(arbo),len(temps))

# print(temps[2])




















                    










    
























        







