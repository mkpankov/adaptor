function(doc) {
	if (doc.series === "series10")
		emit(doc._id, doc);
}