function(doc) { 
	if (doc.doc_type === "ExperimentDocument") 
		emit(doc._id, doc); 
}
