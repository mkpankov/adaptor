function(doc) {
	d = new Date(Date.parse(doc.datetime));
	d1 = new Date("2012-12-28T00:00:00Z")
	d2 = new Date("2012-12-31T00:00:00Z")
	if (doc.doc_type === "ExperimentDocument" &&
		d1 <= d && d <= d2)
		emit(doc._id, doc);
}
