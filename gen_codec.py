class BasicType:
    def __init__(self, rust_name, rust_method, typescript_name, typescript_method):
        self._rust_signature = rust_name
        self._rust_serialize = "type_%s_serialize(&mut out, %%s);" % rust_method
        self._rust_deserialize = "%%s = type_%s_deserialize(&buf, index)?;" % rust_method
        self._typescript_signature = typescript_name
        self._typescript_serialize = "type_%s_serialize(out, %%s);" % typescript_method
        self._typescript_deserialize = "%%s = type_%s_deserialize(buf, index);" % typescript_method
    def rust_signature(self):
        return self._rust_signature
    def rust_serialize(self, name):
        return self._rust_serialize % name
    def rust_deserialize(self, name):
        return self._rust_deserialize % name
    def typescript_signature(self):
        return self._typescript_signature
    def typescript_serialize(self, name):
        return self._typescript_serialize % name
    def typescript_deserialize(self, name):
        return self._typescript_deserialize % name
class OptionType:
    def __init__(self, inner):
        self.inner = inner
        self._rust_signature = "Option<%s>" % inner.rust_signature()
        self._rust_serialize = "if let Some(tmp) = %%s {out.push(1); %s} else {out.push(0);}" % inner.rust_serialize("tmp")
        self._rust_deserialize = "%%s = {if buf[*index] > 0 {*index += 1; let tmp; %s Some(tmp)} else {*index += 1; None}};" % inner.rust_deserialize("tmp")
        self._typescript_signature = "%s|null" % inner.typescript_signature()
    def rust_signature(self):
        return self._rust_signature
    def rust_serialize(self, name):
        return self._rust_serialize % name
    def rust_deserialize(self, name):
        return self._rust_deserialize % name
    def typescript_signature(self):
        return self._typescript_signature
    def typescript_serialize(self, name):
        return "if (%s === null) out.push(0); else {out.push(1); %s};" % (name, self.inner.typescript_serialize(name))
    def typescript_deserialize(self, name):
        return "if (buf[index.v++] > 0) {%s} else {%s = null;}" % (self.inner.typescript_deserialize(name), name)
class EnumType:
    def __init__(self, name):
        self._rust_signature = name
        self._rust_serialize = "%s.serialize(&mut out);"
        self._rust_deserialize = "%%s = %s::deserialize(&buf, index)?;" % name
        self._typescript_signature = name
        self._typescript_serialize = "enum_%s_serialize(out, %%s);" % name
        self._typescript_deserialize = "%%s = enum_%s_deserialize(buf, index);" % name
    def rust_signature(self):
        return self._rust_signature
    def rust_serialize(self, name):
        return self._rust_serialize % name
    def rust_deserialize(self, name):
        return self._rust_deserialize % name
    def typescript_signature(self):
        return self._typescript_signature
    def typescript_serialize(self, name):
        return self._typescript_serialize % name
    def typescript_deserialize(self, name):
        return self._typescript_deserialize % name

TypeString = BasicType("String", "string", "string", "string")
TypeFloat = BasicType("f32", "float", "number", "float")
TypeUShort = BasicType("u16", "u16", "number", "ushort")
TypeFloatPair = BasicType("(f32,f32)", "float_pair", "[number, number]", "float_pair")
TypeUByte = BasicType("u8", "u8", "number", "ubyte")
TypeBoolean = BasicType("bool","bool","boolean","boolean")

class MessageCategory:
    def __init__(self, name):
        self.name = name
        self.messages = []
class Message:
    def __init__(self, name):
        self.name = name
        self.fields = []
class Field:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
class Enum:
    def __init__(self, name, varriants):
        self.name = name
        self.varriants = varriants

categories = []
enums = []

PartKind = Enum("PartKind", [
    "Core",
    "Cargo",
    "LandingThruster",
    "Hub",
])
enums.append(PartKind)
TypePartKind = EnumType("PartKind")


ToServerMsg = MessageCategory("ToServerMsg")
categories.append(ToServerMsg)

Handshake = Message("Handshake")
Handshake.fields.append(Field("client", TypeString))
Handshake.fields.append(Field("session", OptionType(TypeString)))
ToServerMsg.messages.append(Handshake)

SetThrusters = Message("SetThrusters")
SetThrusters.fields.append(Field("forward", TypeBoolean))
SetThrusters.fields.append(Field("backward", TypeBoolean))
SetThrusters.fields.append(Field("clockwise", TypeBoolean))
SetThrusters.fields.append(Field("counter_clockwise", TypeBoolean))
ToServerMsg.messages.append(SetThrusters)

ToClientMsg = MessageCategory("ToClientMsg")
categories.append(ToClientMsg)

HandshakeAccepted = Message("HandshakeAccepted")
HandshakeAccepted.fields.append(Field("id", TypeUShort))
HandshakeAccepted.fields.append(Field("core_id", TypeUShort))
ToClientMsg.messages.append(HandshakeAccepted)

AddCelestialObject = Message("AddCelestialObject")
AddCelestialObject.fields.append(Field("name", TypeString))
AddCelestialObject.fields.append(Field("display_name", TypeString))
AddCelestialObject.fields.append(Field("radius", TypeFloat))
AddCelestialObject.fields.append(Field("id", TypeUShort))
AddCelestialObject.fields.append(Field("position", TypeFloatPair))
ToClientMsg.messages.append(AddCelestialObject)

AddPart = Message("AddPart")
AddPart.fields.append(Field("id", TypeUShort))
AddPart.fields.append(Field("kind", TypePartKind))
ToClientMsg.messages.append(AddPart)

MovePart = Message("MovePart")
MovePart.fields.append(Field("id", TypeUShort))
MovePart.fields.append(Field("x", TypeFloat))
MovePart.fields.append(Field("y", TypeFloat))
MovePart.fields.append(Field("rotation_n", TypeFloat))
MovePart.fields.append(Field("rotation_i", TypeFloat))
ToClientMsg.messages.append(MovePart)

UpdatePartMeta = Message("UpdatePartMeta")
UpdatePartMeta.fields.append(Field("id", TypeUShort))
UpdatePartMeta.fields.append(Field("owning_player", OptionType(TypeUShort)))
UpdatePartMeta.fields.append(Field("thrust_mode", TypeUByte))
ToClientMsg.messages.append(UpdatePartMeta)

RemovePart = Message("RemovePart")
RemovePart.fields.append(Field("id", TypeUShort))
ToClientMsg.messages.append(RemovePart)

AddPlayer = Message("AddPlayer")
AddPlayer.fields.append(Field("id", TypeUShort))
AddPlayer.fields.append(Field("name", TypeString))
ToClientMsg.messages.append(AddPlayer)

UpdatePlayer = Message("UpdatePlayer")
UpdatePlayer.fields.append(Field("id", TypeUShort))
UpdatePlayer.fields.append(Field("thrust_forward", TypeBoolean))
UpdatePlayer.fields.append(Field("thrust_backward", TypeBoolean))
UpdatePlayer.fields.append(Field("thrust_clockwise", TypeBoolean))
UpdatePlayer.fields.append(Field("thrust_counter_clockwise", TypeBoolean))
ToClientMsg.messages.append(UpdatePlayer)

RemovePlayer = Message("RemovePlayer")
RemovePlayer.fields.append(Field("id", TypeUShort))
ToClientMsg.messages.append(RemovePlayer)

rust_header = open("codec_header.rs", "r")
rust_out = open("codec.rs", "w")
rust_out.write(rust_header.read())
rust_out.write("\n\n")
rust_header.close()
for enum in enums:
    rust_out.write("#[derive(Copy, Clone)] pub enum %s {\n\t%s\n}\n" % (enum.name, ", ".join(enum.varriants)))
    rust_out.write("impl %s {\n\tpub fn serialize(&self, buf: &mut Vec<u8>) {\n\t\tbuf.push(match self {\n\t\t\t%s\n\t\t});\n\t}\n" % (enum.name, ", ".join(map(lambda varriant: "Self::%s => %s" % (varriant[1], varriant[0]), enumerate(enum.varriants)))))
    rust_out.write("\tpub fn deserialize(buf: &[u8], index: &mut usize) -> Result<Self, ()> {\n\t\tlet me = buf[*index]; *index += 1;\n\t\tmatch me {\n\t\t\t%s,\n\t\t\t_ => Err(())\n\t\t}\n\t}\n}\n" % ", ".join(map(lambda varriant: "%s => Ok(Self::%s)" % (varriant[0], varriant[1]), enumerate(enum.varriants))))
rust_out.write("\n")
for category in categories:
    rust_out.write("pub enum %s {\n" % category.name)
    for message in category.messages:
        if len(message.fields) > 0:
            rust_out.write("\t%s { " % message.name)
            for field in message.fields:
                rust_out.write("%s: %s, " % (field.name, field.kind.rust_signature()))
            rust_out.write("},\n")
        else:
            rust_out.write("\t%s,\n" % message.name)
    rust_out.write("}\nimpl %s {\n\tpub fn serialize(&self) -> Vec<u8> {\n\t\tlet mut out: Vec<u8> = Vec::new();\n\t\tmatch self {\n" % category.name)
    for i, message in enumerate(category.messages):
        rust_out.write("\t\t\tSelf::%s { %s} => {\n\t\t\t\tout.push(%s);\n" % (message.name, ", ".join(map(lambda field: field.name, message.fields)), str(i)))
        for field in message.fields:
            rust_out.write("\t\t\t\t%s\n" % field.kind.rust_serialize(field.name))
        rust_out.write("\t\t\t},\n")
    rust_out.write("\t\t};\n\t\tout\n\t}\n\tpub fn deserialize(buf: &[u8], index: &mut usize) -> Result<Self,()> {\n\t\tlet i = *index;\n\t\t*index += 1;\n\t\tmatch buf[i] {\n")
    for i, message in enumerate(category.messages):
        rust_out.write("\t\t\t%s => {\n\t\t\t\t%s\n" % (str(i), " ".join(map(lambda field: ("let %s;" % field.name), message.fields))))
        for field in message.fields:
            rust_out.write("\t\t\t\t%s\n" % field.kind.rust_deserialize(field.name))
        rust_out.write("\t\t\t\tOk(%s::%s { %s})\n\t\t\t},\n" % (category.name, message.name, ", ".join(map(lambda field: field.name, message.fields))))
    rust_out.write("\t\t\t_ => Err(())\n\t\t}\n\t}\n}\n\n")
rust_out.close()

typescript_header = open("codec_header.ts", "r")
typescript_out = open("codec.ts", "w")
typescript_out.write(typescript_header.read())
typescript_out.write("\n\n")
typescript_header.close()
for enum in enums:
    typescript_out.write("export enum %s {\n\t%s\n}\n" % (enum.name, ", ".join(enum.varriants)))
    typescript_out.write("function enum_%s_serialize(buf: number[], val: %s) { buf.push(val as number); }" % (enum.name, enum.name));
    typescript_out.write("function enum_%s_deserialize(buf: Uint8Array, index: Box<number>): %s {\n\tconst me = buf[index.v++];\n\tif (me < %s) return me as %s;\n\telse throw new Error('Bad %s deserialize');\n}\n" % (enum.name, enum.name, len(enum.varriants), enum.name, enum.name))
    #typescript_out.write("function enum_%s_deserialize(buf: Uint8Array, index: Box<number>): %s {\n\tswitch (buf[index.v++]) {\n\t\t%s\n\t\tdefault: throw new Error('Bad %s varriant');\n\t}\n}\n" % (enum.name, enum.name, " ".join(map(lambda varriant: "case %s: return %s.%s;" % (varriant[0], enum.name, varriant[1]), enumerate(enum.varriants))), enum.name))
typescript_out.write("\n")
for category in categories:
    for i, message in enumerate(category.messages):
        typescript_out.write("class %s_%s {\n\tstatic readonly id = %s;\n" % (category.name, message.name, i))
        typescript_out.write("\t%s\n\tconstructor(%s) {\n\t\t%s\n\t}\n" % (
            " ".join(map(lambda field: "%s: %s;" % (field.name, field.kind.typescript_signature()), message.fields)),
            " ".join(map(lambda field: "%s: %s," % (field.name, field.kind.typescript_signature()), message.fields)),
            " ".join(map(lambda field: "this.%s = %s;" % (field.name, field.name), message.fields))
        ))
        typescript_out.write("\tserialize(): Uint8Array\n\t\t{let out = [%s];\n" % i)
        for field in message.fields:
            typescript_out.write("\t\t%s\n" % field.kind.typescript_serialize("this." + field.name))
        typescript_out.write("\t\treturn new Uint8Array(out);\n\t}\n}\n")
    typescript_out.write("function deserialize_%s(buf: Uint8Array, index: Box<number>) {\n\tswitch (buf[index.v++]) {\n" % category.name)
    for i, message in enumerate(category.messages):
        typescript_out.write("\t\tcase %s: {\n\t\t\t%s\n" % (i, " ".join(map(lambda field: "let %s: %s;" % (field.name, field.kind.typescript_signature()), message.fields))))
        for field in message.fields:
            typescript_out.write("\t\t\t%s\n" % field.kind.typescript_deserialize(field.name))
        typescript_out.write("\t\t\treturn new %s_%s(%s);\n\t\t}; break;" % (category.name, message.name, ", ".join(map(lambda field: field.name, message.fields))))
    typescript_out.write("\t\tdefault: throw new Error();\n\t}\n}\nexport const %s = {\n\tdeserialize: deserialize_%s,\n\t%s\n};\n\n" % (
        category.name, category.name,
        ", ".join(map(lambda message: "%s: %s_%s" % (message.name, category.name, message.name), category.messages))
    ))
typescript_out.close()
    
