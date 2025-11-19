import pymupdf4llm

def split_path(path): 
    s=path.split("/")
    if len(s)==1 : s=path.split("\\")
    return s


def pdf_to_markdown(path,sep="\\"):

    splitted_path=split_path(path)

    root,name=splitted_path[:-1],splitted_path[-1].split(".")[0]+".md"

    dest_path=f"{sep}".join(root+[name])
    
    with open(dest_path,"w",encoding="utf-8") as file : 
        file.write(pymupdf4llm.to_markdown(path))

    return dest_path

def get_next_chunk (file,size,overflow="") : 

    chunk=overflow+file.read(size)
    lignes=chunk.split("\n")
    overflow=lignes[-1]

    return lignes[:-1],overflow


def is_title(string):

    return  True if len(string) > 0 and string[0]=="#" else False


def calculate_indent (string) : 

    indent=0
    for x in string : 
        if x!='#' : return indent
        else : indent+=1

    return indent

def parse_markdown (path) : 

    arbo=[]
    cursor=[]
    temps=[]
    

    with open (path,"r",encoding="utf-8") as file : 

        temp=[]
        overflow=""

        while True :

            lignes,overflow=get_next_chunk(file,4094,overflow)
            if len(lignes)==0: break 

            for l in lignes : 
  
                if is_title(l)==True:

                    t= cursor[-1] if len(cursor)>0 else ""

                    current_title_indent=calculate_indent(l)
                    last_title_indent=calculate_indent(t)

                    if last_title_indent<current_title_indent : 
                       
                        if temp!=[] :
                            arbo+=[cursor]
                            temps+=[temp]
                            temp=[]

                    
                        
                        cursor=cursor+[l]    
                       
                        
                        
                       

                    elif last_title_indent==current_title_indent : 

                        arbo+=[cursor]
                        temps+=[temp]

                        cursor=cursor[:-1]+[l]

                       

                        temp=[]
                    
                       

                    else : 
                        
                        arbo+=[cursor]
                        cursor=cursor[:current_title_indent-1]+[l]
                        temps+=[temp]
                        
                        temp=[]
                        

                else : 
                    if l!="" :temp+=[l]
                    
      
                    
    arbo+=[cursor]
    temps+=[temp]

    return arbo,temps


