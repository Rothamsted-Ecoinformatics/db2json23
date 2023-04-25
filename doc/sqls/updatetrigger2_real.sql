CREATE   TRIGGER trg_PairedRI 
ON cdERA.[cdm ].related_identifiers
AFTER INSERT, DELETE, UPDATE
AS
BEGIN		
 	-- SET NOCOUNT ON; I am not sure I need that
 	
	DECLARE @ori_ri_ID INT -- the relashionship ID
	DECLARE @ori_md INT		-- the original dataset or document
	DECLARE @ori_DOI VARCHAR (100)	-- the original document DOI : will be in the database. 
	DECLARE @ori_name VARCHAR(100)	-- the title of the Original document or dataset. 
		
	DECLARE @RI_DOI VARCHAR(100)	-- the related identifier  DOI - just inserted - might be in the database or not
	DECLARE @RI_md 	INT				-- the md_id of the related identifier if in the database (you have the DOI, get the md_id)
	DECLARE @RI_name VARCHAR(100)	-- the title of the RI inserted if the RI is in the database
		
	DECLARE @ori_rt_ID INT	-- relation type ori_md --> ori_RI 
 	DECLARE @pair_rt_ID INT 		-- opposite relation type
 	
 	DECLARE @pair_ri_ID INT 	-- opposite relation connection
 	
 	DECLARE @DEBUGMESSAGE  VARCHAR(8000) = N'Main Degugging
'
 	DECLARE @DEBUGNEW  VARCHAR(8000) = N'New Degugging
'
	IF EXISTS ( SELECT 0 FROM Deleted )
		BEGIN	
			IF EXISTS ( SELECT 0 FROM Inserted )
				-- something updated
				BEGIN
					SELECT  @ori_md = md_id, @RI_DOI = related_identifier, @ori_rt_ID = rt_id
		    		FROM    Inserted d	
		    	
					-- find ori_DOI
					SELECT @ori_DOI = identifier, @ori_name = title from metadata_document where md_id = @ori_md 	    	
				
				    -- find the elements for the paired identifier: these will be included in either an update or insert or delete query
					SELECT  @pair_rt_ID = pair_id from relation_types where rt_id = @ori_rt_ID
				
					SET @DEBUGMESSAGE +=  'Point 0
	 				@ori_DOI =    ' + @ori_DOI  + ' 
					'
	 				SET @DEBUGMESSAGE += '
	 				@ori_rt_ID =  ' + convert(varchar(10),  @ori_rt_ID	)
	 
	  				SET @DEBUGMESSAGE += '
					@pair_rt_ID  =  ' + convert(varchar(10),  @pair_rt_ID 	)
	 				SET @DEBUGMESSAGE += '
	 				@ori_md  =  ' + convert(varchar(100),  @ori_md 	)
				    -- find out if the @ori_RI is in my database.
				
	 				SET @DEBUGMESSAGE += '
					'   			    	
			    	IF EXISTS ( SELECT 0 from metadata_document where identifier = @RI_DOI )	
			    		-- finding that the document is in our database and update the paired relation if it needs updating
					   BEGIN
						   SELECT @RI_md = md_id from metadata_document where identifier = @RI_DOI
						   SET @DEBUGMESSAGE +=  'Point 1
								'    
							-- In this block, a related identifier has been updated (one record deleted, one inserted) so the paired one should be here and either be updated or no change. 
					       SET @DEBUGMESSAGE += '
							Something updated ' + convert(varchar(100),@RI_DOI) + ' '+ convert(varchar(10),@ori_rt_ID)
					       
					                   
						   IF EXISTS (SELECT  0 from related_identifiers where md_id = @RI_md and related_identifier = @ori_DOI)
				    			BEGIN
					    			SELECT  @pair_ri_ID = ri_id from related_identifiers where md_id = @RI_md and related_identifier = @ori_DOI	
					    			SET @DEBUGNEW += '
	 								@pair_ri_ID  =  ' + convert(varchar(100),  @pair_ri_ID 	) + 'is already here'
													-- we have found that there is already a connection between these elements. We just want to check that the connection between them is the correct one. 
					    			IF EXISTS (SELECT 0 from related_identifiers where md_id = @RI_md and related_identifier = @ori_DOI and rt_id =  @pair_rt_ID)
					    				BEGIN
											SET @DEBUGMESSAGE += '
											-- the connection is correct: do nothing'
					    				END 
					    			ELSE
					    				BEGIN
						    				SET @DEBUGMESSAGE += '
											-- update the connection'
						    				
											UPDATE related_identifiers SET md_id=@RI_md, related_identifier=@ori_DOI, it_id=1, rt_id=@pair_rt_ID WHERE ri_id=@pair_ri_ID
					    				END 
				    			END 
				    		ELSE
				    			BEGIN
					    			SET @DEBUGNEW += '
									paired is missing - development mode
											'
				    			END				                   			
					     END
					ELSE
					     BEGIN
						     SET @DEBUGNEW += '
								-- the related identifier is not in the database, so nothing to do'
					     END 
				END
			ELSE
				BEGIN
				                   
					SET @DEBUGMESSAGE +=  '
						Something DELETED - delete the pair if it exists'
					SELECT  @ori_md = md_id, @RI_DOI = related_identifier, @ori_rt_ID = rt_id
		    		FROM    Deleted d	
		    	
						-- find ori_DOI
					SELECT @ori_DOI = identifier from metadata_document where md_id = @ori_md 	    	
				
				    -- find the elements for the paired identifier: these will be included in either an update or insert or delete query
					SELECT  @pair_rt_ID = pair_id from relation_types where rt_id = @ori_rt_ID
					
					
				
					SET @DEBUGMESSAGE +=  'Point 0
	 				@ori_DOI =    ' + @ori_DOI  + ' 
					'
	 				SET @DEBUGMESSAGE += '
	 				@ori_rt_ID =  ' + convert(varchar(10),  @ori_rt_ID	)
	 
	  				SET @DEBUGMESSAGE += '
					@pair_rt_ID  =  ' + convert(varchar(10),  @pair_rt_ID 	)
	 				SET @DEBUGMESSAGE += '
	 				@ori_md  =  ' + convert(varchar(100),  @ori_md 	)
				    -- find out if the @ori_RI is in my database.
				
	 				SET @DEBUGMESSAGE += '
					'   			    	                
					                   
					IF EXISTS (SELECT 0 from metadata_document where identifier = @RI_DOI )
					    BEGIN
						   	SELECT @RI_md = md_id from metadata_document where identifier = @RI_DOI             
					       	SELECT  @pair_ri_ID = ri_id from related_identifiers where md_id = @RI_md and related_identifier = @ori_DOI
						   	-- delete the opposite connection if it is there 
						   
							
							DELETE FROM related_identifiers WHERE ri_id =  @pair_ri_ID
					    END 
				
				END 
		END
    ELSE
        BEGIN 
	        
            SET @DEBUGMESSAGE +=  '
			Something INSERTED'
           
            
            SELECT  @ori_ri_ID = ri_id, @ori_md = md_id, @RI_DOI = related_identifier, @ori_rt_ID = rt_id
    		FROM    inserted i 
    		SET @DEBUGMESSAGE +=  ' 
				inserted ' + convert(varchar(100),@RI_DOI) + ' '+ convert(varchar(10),@ori_rt_ID)		    	
		   	 --  find ori_DOI
			SELECT @ori_DOI = identifier, @ori_name = title  from metadata_document where md_id = @ori_md 
			    	
		    SELECT  @pair_rt_ID = pair_id from relation_types where rt_id = @ori_rt_ID
		    -- first we find out if that DOI we have just added is one our our documents 
		    SELECT @RI_md = md_id, @RI_name = title  from metadata_document where identifier = @RI_DOI		    
		    
		    IF EXISTS ( SELECT 0 from metadata_document where identifier = @RI_DOI )
		    	BEGIN
				    -- what does the opposing 
				    -- we find out if the connection is already added or not
				    				  
				    IF EXISTS ( SELECT  0 from related_identifiers where md_id = @RI_md and related_identifier = @ori_DOI )	
				    	BEGIN
						    SELECT  @pair_ri_ID = ri_id from related_identifiers where md_id = @RI_md and related_identifier = @ori_DOI						    	
						    	
							UPDATE related_identifiers
							SET md_id=  @RI_md , related_identifier=  @ori_DOI , it_id=0, rt_id= @pair_rt_ID, ri_name = @ori_name 
							WHERE ri_id=  @pair_ri_ID
							
							UPDATE related_identifiers
							SET  ri_name = @RI_name 
							WHERE ri_id=  @ori_ri_ID
												    		
				    	END 
				    ELSE
				    	BEGIN
					    	SET @DEBUGMESSAGE +=  '-- insert the new connection'		
					    	INSERT INTO related_identifiers
								(md_id, related_identifier, it_id, rt_id, ri_name)
								VALUES(@RI_md, @ori_DOI, 1, @pair_rt_ID, @ori_name);
							UPDATE related_identifiers
							SET  ri_name = @RI_name 
							WHERE ri_id=  @ori_ri_ID
				    	END 
		    	END  
		    ELSE
				BEGIN					     	
					   SET @DEBUGMESSAGE +=  '
						-- the added identifier is not in the database, so there is nothing to do'
				END 
        END	
PRINT @DEBUGMESSAGE
PRINT @DEBUGNEW
END
;
