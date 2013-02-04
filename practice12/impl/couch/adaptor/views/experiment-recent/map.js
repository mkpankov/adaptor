function(doc) {
	d = new Date();
	if (doc.doc_type === "ExperimentDocument" && 
		d.getTime() - Date.parse(doc.datetime) < 1000000)
		emit(doc._id, doc);
}